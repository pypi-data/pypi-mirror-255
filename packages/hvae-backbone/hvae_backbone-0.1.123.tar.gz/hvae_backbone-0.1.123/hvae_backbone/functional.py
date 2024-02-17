import logging
import time

import numpy as np
import torch
from torch import tensor
from torch.utils.data import DataLoader
import wandb

from .checkpoint import Checkpoint
from .utils import linear_temperature, prepare_for_log, print_line, wandb_log_results

from . import params


def compute_loss(targets: tensor, distributions: dict, logits: tensor = None, step_n: int = 0) -> dict:
    """
    Compute loss for VAE (custom or default)
    based on Efficient-VDVAE paper

    :param targets: tensor, the target images
    :param distributions: list, the distributions for each generator block
    :param logits: tensor, the logits for the output block
    :param step_n: int, the current step number
    :return: dict, containing the loss values

    """

    # Use custom loss funtion if provided
    if params.loss_params.custom_loss is not None:
        return params.loss_params.custom_loss(targets=targets, logits=logits,
                                              distributions=distributions, step_n=step_n)

    output_distribution = distributions['output']
    feature_matching_loss = params.reconstruction_loss(targets, output_distribution)

    global_variational_prior_losses = []
    kl_divs = dict()
    for block_name, dists in distributions.items():
        if block_name == 'output' or dists is None or len(dists) != 2 or dists[1] is None:
            continue
        prior, posterior = dists
        loss = params.kl_divergence(prior, posterior)
        global_variational_prior_losses.append(loss)
        kl_divs.update({block_name: loss})

    global_variational_prior_losses = torch.stack(global_variational_prior_losses)
    kl_div = torch.sum(global_variational_prior_losses)  # / np.log(2.)
    global_variational_prior_loss = kl_div \
        if not params.loss_params.use_gamma_schedule \
        else params.gamma_schedule(global_variational_prior_losses, step_n=step_n)
    global_var_loss = params.kldiv_schedule(step_n) * global_variational_prior_loss  # beta
    elbo = feature_matching_loss - global_var_loss

    return dict(
        elbo=elbo,
        reconstruction_loss=-feature_matching_loss,
        kl_div=kl_div,
        #kl_divs=kl_divs,
    )


def gradient_norm(net):
    """
    Compute the global norm of the gradients of the network parameters
    based on Efficient-VDVAE paper
    :param net: hVAE, the network
    """
    parameters = [p for p in net.parameters() if p.grad is not None and p.requires_grad]
    if len(parameters) == 0:
        total_norm = torch.tensor(0.0)
    else:
        device = parameters[0].grad.device
        total_norm = torch.norm(torch.stack([torch.norm(p.grad.detach(), 2.0).to(device) for p in parameters]), 2.0)
    return total_norm


def gradient_clip(net):
    """
    Clip the gradients of the network parameters
    based on Efficient-VDVAE paper
    """
    if params.optimizer_params.clip_gradient_norm:
        total_norm = torch.nn.utils.clip_grad_norm_(net.parameters(),
                                                    max_norm=params.optimizer_params.gradient_clip_norm_value)
    else:
        total_norm = gradient_norm(net)
    return total_norm


def gradient_skip(global_norm):
    """
    Skip the gradient update if the global norm is too high
    based on Efficient-VDVAE paper
    :param global_norm: tensor, the global norm of the gradients
    """
    if params.optimizer_params.gradient_skip:
        if torch.any(torch.isnan(global_norm)) or global_norm >= params.optimizer_params.gradient_skip_threshold:
            skip = True
            gradient_skip_counter_delta = 1.
        else:
            skip = False
            gradient_skip_counter_delta = 0.
    else:
        skip = False
        gradient_skip_counter_delta = 0.
    return skip, gradient_skip_counter_delta


def reconstruction_step(net, inputs: tensor, step_n=None, use_mean=False):
    """
    Perform a reconstruction with the given network and inputs
    based on Efficient-VDVAE paper

    :param net: hVAE, the network
    :param inputs: tensor, the input images
    :param step_n: int, the current step number
    :param use_mean: use the mean of the distributions instead of sampling
    :return: tensor, tensor, dict, the output images, the computed features, the loss values
    """
    net.eval()
    with torch.no_grad():
        computed, distributions = net(inputs, use_mean=use_mean)
        if step_n is None:
            step_n = max(params.loss_params.vae_beta_anneal_steps, params.loss_params.gamma_max_steps) * 10.
        results = compute_loss(inputs, distributions, step_n=step_n)
        return computed, distributions, results


def reconstruct(net, dataset: DataLoader, wandb_run: wandb.run,
                use_mean, global_step=None, logger: logging.Logger = None):
    """
    Reconstruct the images from the given dataset
    based on Efficient-VDVAE paper

    :param net: hVAE, the network
    :param dataset: DataLoader, the dataset
    :param wandb_run: wandb run object
    :param use_mean: use the mean of the distributions instead of sampling
    :param global_step: int, the current step number
    :param logger: logging.Logger, the logger
    :return: list, the input/output pairs
    """

    # Evaluation
    n_samples_for_eval = params.eval_params.n_samples_for_validation
    results, (original, output_samples, output_means) = \
        evaluate(net, dataset, n_samples=n_samples_for_eval, use_mean=use_mean, global_step=global_step, logger=logger)

    # Reconstruction
    n_samples_for_reconstruct = params.eval_params.n_samples_for_reconstruction
    for i in range(n_samples_for_reconstruct):
        o = wandb.Image(original[i].reshape(params.data_params.shape), caption=f'Original {i}')
        s = wandb.Image(output_samples[i].reshape(params.data_params.shape), caption=f'Sample {i}')
        m = wandb.Image(output_means[i].reshape(params.data_params.shape), caption=f'Mean {i}')
        wandb_run.log({f"reconstruction_{i}": [o, s, m]}, step=global_step)

    test_table = wandb.Table(data=[list(prepare_for_log(results).values())], columns=list(results.keys()))
    wandb_run.log({"test": test_table}, step=global_step)

    return results


def generate(net, logger: logging.Logger):
    """
    Generate images with the given network
    based on Efficient-VDVAE paper

    :param net: hVAE, the network
    :param logger: logging.Logger, the logger
    :return: list, the generated images
    """
    all_outputs = list()
    for temp_i, temperature_setting in enumerate(params.analysis_params.generation.temperature_settings):
        logger.info(f'Generating for temperature setting {temp_i:01d}')
        if isinstance(temperature_setting, list):
            temperatures = temperature_setting

        elif isinstance(temperature_setting, float):
            temperatures = [temperature_setting] * len(net.blocks)

        elif isinstance(temperature_setting, tuple):
            # Fallback to function defined temperature.
            # Function params are defined with 3 arguments in a tuple
            assert len(temperature_setting) == 3
            down_blocks = len(net)
            temp_fn = linear_temperature(*(temperature_setting[1:]), n_layers=down_blocks)
            temperatures = [temp_fn(layer_i) for layer_i in range(down_blocks)]

        else:
            logger.error(f'Temperature Setting {temperature_setting} not interpretable!!')
            raise ValueError(f'Temperature Setting {temperature_setting} not interpretable!!')

        temp_outputs = list()
        for step in range(params.analysis_params.generation.n_generation_batches):
            computed, _ = net.sample_from_prior(
                params.analysis_params.batch_size, temperatures=temperatures)
            temp_outputs.append(computed['output'])
        all_outputs.append(temp_outputs)
    return all_outputs


def train_step(net, optimizer, schedule, inputs, step_n):
    """
    Perform a training step with the given network and inputs
    based on Efficient-VDVAE paper

    :param net: hVAE, the network
    :param optimizer: torch.optim.Optimizer, the optimizer
    :param schedule: torch.optim.lr_scheduler.LRScheduler, the scheduler
    :param inputs: tensor, the input images
    :param step_n: int, the current step number
    :return: tensor, dict, tensor, the output images, the loss values, the global norm of the gradients
    """
    computed, distributions = net(inputs)
    output_sample = computed['output']
    results = compute_loss(inputs, distributions, step_n=step_n)

    nelbo = -results["elbo"]
    nelbo.backward()

    global_norm = gradient_clip(net)
    skip, gradient_skip_counter_delta = gradient_skip(global_norm)

    if not skip:
        optimizer.step()
        schedule.step()

    optimizer.zero_grad()
    return output_sample, results, global_norm, gradient_skip_counter_delta


def train(net,
          optimizer, schedule,
          train_loader: DataLoader, val_loader: DataLoader,
          start_step: int, wandb_run: wandb.run,
          checkpoint_path: str, logger: logging.Logger) -> None:
    """
    Train the network
    based on Efficient-VDVAE paper

    :param net: hVAE, the network
    :param optimizer: torch.optim.Optimizer, the optimizer
    :param schedule: torch.optim.lr_scheduler.LRScheduler, the scheduler
    :param train_loader: DataLoader, the training dataset
    :param val_loader: DataLoader, the validation dataset
    :param start_step: int, the step number to start from
    :param wandb_run: wandb run object
    :param checkpoint_path: str, the path to save the checkpoints to
    :param logger: logging.Logger, the logger
    :return: None
    """
    global_step = start_step
    gradient_skip_counter = 0.

    total_train_epochs = int(np.ceil(params.train_params.total_train_steps / len(train_loader)))
    for epoch in range(total_train_epochs):
        for batch_n, train_inputs in enumerate(train_loader):
            net.train()
            global_step += 1
            train_inputs = train_inputs.to(params.device, non_blocking=True)
            start_time = time.time()
            train_outputs, train_results, global_norm, gradient_skip_counter_delta = \
                train_step(net, optimizer, schedule, train_inputs, global_step)
            end_time = round((time.time() - start_time), 2)
            gradient_skip_counter += gradient_skip_counter_delta

            train_results.update({
                "time": end_time,
                "beta": params.kldiv_schedule(global_step),
                "grad_norm": global_norm,
                "grad_skip_count": gradient_skip_counter,
            })
            train_results = prepare_for_log(train_results)
            logger.info((global_step,
                         ('Time/Step (sec)', end_time),
                         ('ELBO', round(train_results["elbo"], 4)),
                         ('Reconstruction Loss', round(train_results["reconstruction_loss"], 3)),
                         ('KL loss', round(train_results["kl_div"], 3))))
            wandb_log_results(wandb_run, train_results, global_step, mode='train')

            """
            EVALUATION AND CHECKPOINTING
            """
            net.eval()
            first_step = global_step == 0
            last_step = global_step == params.train_params.total_train_steps - 1
            eval_time = global_step % params.log_params.eval_interval_in_steps == 0
            checkpoint_time = global_step % params.log_params.checkpoint_interval_in_steps == 0
            if eval_time or checkpoint_time:
                print_line(logger, newline_after=False)

            if eval_time or first_step or last_step:
                train_ssim = params.ssim_metric(train_inputs, train_outputs,
                                                global_batch_size=params.train_params.batch_size)
                logger.info(
                    f'Train Stats | '
                    f'ELBO {train_results["elbo"]} | '
                    f'Reconstruction Loss {train_results["reconstruction_loss"]:.4f} |'
                    f'KL Div {train_results["kl_div"]:.4f} |'
                    f'SSIM: {train_ssim}')
                val_results = reconstruct(net, val_loader, wandb_run,
                                          use_mean=params.eval_params.use_mean,
                                          global_step=global_step, logger=logger)
                val_results = prepare_for_log(val_results)

                wandb_log_results(wandb_run, {'train_ssim': train_ssim}, global_step, mode='train')
                wandb_log_results(wandb_run, val_results, global_step, mode='validation')

            if checkpoint_time or last_step:
                # Save checkpoint (only if better than best)
                experiment = Checkpoint(global_step, net, optimizer, schedule, params)
                path = experiment.save(checkpoint_path, wandb_run)
                logger.info(f'Saved checkpoint for global_step {global_step} to {path}')

            if eval_time or checkpoint_time:
                print_line(logger, newline_after=True)

            if global_step >= params.train_params.total_train_steps:
                logger.info(f'Finished training after {global_step} steps!')
                return


def evaluate(net, val_loader: DataLoader, n_samples: int, global_step: int = None,
             use_mean=False, logger: logging.Logger = None) -> tuple:
    """
    Evaluate the network on the given dataset

    :param net: hVAE, the network
    :param val_loader: DataLoader, the dataset
    :param n_samples: number of samples to evaluate
    :param global_step: int, the current step number
    :param use_mean: use the mean of the distributions instead of sampling
    :param logger: logging.Logger, the logger
    :return: dict, tensor, tensor, the loss values, the output images, the input images
    """
    net.eval()

    val_step = 0
    global_results, original, output_samples, output_means = None, None, None, None
    for val_step, val_inputs in enumerate(val_loader):
        n_samples -= params.eval_params.batch_size
        val_inputs = val_inputs.to(params.device, non_blocking=True)
        val_computed, val_distributions, val_results = \
            reconstruction_step(net, inputs=val_inputs, step_n=global_step, use_mean=use_mean)
        val_outputs = val_computed["output"]
        val_output_means = val_distributions['output'].mean
        val_results["ssim"] = params.ssim_metric(val_inputs, val_outputs,
                                                 params.eval_params.batch_size).detach().cpu()
        val_results["mean_ssim"] = params.ssim_metric(val_inputs, val_output_means,
                                                      params.eval_params.batch_size).detach().cpu()

        val_inputs = val_inputs.detach().cpu()
        val_outputs = val_outputs.detach().cpu()
        val_output_means = val_output_means.detach().cpu()
        if global_results is None:
            global_results = val_results
            original = val_inputs
            output_samples = val_outputs
            output_means = val_output_means
        else:
            global_results = {k: v + val_results[k] for k, v in global_results.items()}
            original = torch.cat((original, val_inputs), dim=0)
            output_samples = torch.cat((output_samples, val_outputs), dim=0)
            output_means = torch.cat((output_means, val_output_means), dim=0)

        if n_samples <= 0:
            break

    global_results = {k: v / (val_step + 1) for k, v in global_results.items()}
    global_results["avg_elbo"] = global_results["elbo"]
    global_results["elbo"] = -global_results["kl_div"] - global_results["reconstruction_loss"]

    log = logger.info if logger is not None else print
    log(
        f'Validation Stats |'
        f' ELBO {global_results["elbo"]:.6f} |'
        f' Reconstruction Loss {global_results["reconstruction_loss"]:.4f} |'
        f' KL Div {global_results["kl_div"]:.4f} |'
        f' SSIM: {global_results["ssim"]:.6f}')

    return global_results, (original, output_samples, output_means)


def extrapolate(net, loader: DataLoader, seq_len, n_samples):
    net.eval()
    original, output_samples, output_means = None, None, None
    for val_step, val_inputs in enumerate(loader):
        n_samples -= params.eval_params.batch_size
        val_inputs = val_inputs.to(params.device, non_blocking=True)
        computed, distributions = net.extrapolate(val_inputs, seq_len=seq_len)
        val_outputs = computed["output"]
        val_output_means = distributions['output'].mean

        val_inputs = val_inputs.detach().cpu()
        val_outputs = val_outputs.detach().cpu()
        val_output_means = val_output_means.detach().cpu()
        if original is None:
            original = val_inputs
            output_samples = val_outputs
            output_means = val_output_means
        else:
            original = torch.cat((original, val_inputs), dim=0)
            output_samples = torch.cat((output_samples, val_outputs), dim=0)
            output_means = torch.cat((output_means, val_output_means), dim=0)

        if n_samples <= 0:
            break
    return original, output_samples, output_means


def model_summary(net):
    """
    Print the model summary
    :param net: nn.Module, the network
    :return: None
    """
    from torchinfo import summary
    shape = (1,) + params.data_params.shape
    return summary(net, input_size=shape, depth=8)