import logging
import math

import numpy as np
import torch
import wandb
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure


from . import params


def generation(model, wandb_run, logger: logging.Logger):
    from .functional import generate

    logger.info('Generating Samples from Prior')
    outputs = generate(model, logger)
    for temp_i, temp_outputs in enumerate(outputs):
        samples = []
        for sample_i, output in enumerate(temp_outputs):
            sample = wandb.Image(output, caption=f'Prior sample {sample_i}')
            samples.append(sample)
        wandb_run.log({f"generation {temp_i}": samples}, step=temp_i)
    logger.info(f'Generation successful')


def extrapolate(model, loader, wandb_run, logger: logging.Logger):
    from .functional import extrapolate
    logger.info('Generating Samples with Extrapolation')
    n_samples = params.analysis_params.extrapolation.n_samples
    seq_len = params.analysis_params.extrapolation.seq_len
    original, samples, means = extrapolate(model, loader, seq_len, n_samples)
    shape = (params.data_params.shape[0] + seq_len, *params.data_params.shape[1:])
    for i in range(n_samples):
        o = wandb.Image(original[i].reshape(params.data_params.shape), caption=f'Original {i}')
        s = wandb.Image(samples[i].reshape(shape), caption=f'Sample {i}')
        m = wandb.Image(means[i].reshape(shape), caption=f'Mean {i}')
        wandb_run.log({f"extrapolation_{i}": [o, s, m]})
    logger.info(f'Extrapolation generation successful')


def mei(model, wandb_run, logger: logging.Logger):
    logger.info('Generating Most Exciting Inputs (MEI)')
    for op_name, op in params.analysis_params.mei.items():
        result = generate_mei(model, op["objective"], op["use_mean"],
                              op["type"], op["config"])
        vis = result.get_image().detach().cpu().numpy()
        wandb_run.log({f"MEI {op_name}": wandb.Image(vis)})
    logger.info(f'MEI generation successful')


def generate_mei(model, objective, use_mean, mei_type, mei_config):
    from meitorch.mei import MEI

    def operation(inputs):
        computed, _ = model(inputs, use_mean=use_mean)
        objective_result = objective(computed)
        if isinstance(objective_result, torch.Tensor):
            return dict(objective=-objective_result,
                        activation=objective_result)
        elif isinstance(objective_result, dict):
            assert 'objective' in objective_result and 'activation' in objective_result, \
                'objective_result must contain keys "objective" and "activation"'
            return objective_result
    mei_object = MEI(operation=operation, shape=params.data_params.shape)

    if mei_type == 'pixel':
        results = mei_object.generate_pixel_mei(**mei_config)
    elif mei_type == 'distribution':
        results = mei_object.generate_variational_mei(**mei_config)
    elif mei_type == 'transform':
        results = mei_object.generate_transformation_based(**mei_config)
    else:
        raise ValueError(f'Unknown MEI type {mei_type}')
    return results


def white_noise_analysis(model, wandb_run, logger: logging.Logger):
    logger.info('Generating Samples with White Noise Analysis')
    shape = params.data_params.shape
    for target_block, config in params.analysis_params.white_noise_analysis.items():
        n_samples = config['n_samples']
        sigma = config['sigma']
        receptive_fields = \
            generate_white_noise_analysis(model, target_block, shape, n_samples, sigma)
        n_dims = receptive_fields.shape[0]
        dims_per_image = np.prod(shape[-2:]) // 20
        n_images = n_dims // dims_per_image + 1

        for im in range(n_images):
            n_dims_im = min(dims_per_image, n_dims - im * dims_per_image)
            start_dim = im * dims_per_image
            n_rows = math.ceil(n_dims_im / 20)
            w = int(shape[-2])
            h = int(shape[-1] / 20 * n_rows)

            fig = figure(figsize=(w, h))
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
            for i in range(n_dims_im):
                ax = fig.add_subplot(n_rows, 20, i + 1)
                ax.imshow(receptive_fields[start_dim + i].reshape(params.data_params.shape[-2:]), cmap="gray")
                ax.set_title(f"dim {i}")
                ax.axis("off")

            fig.tight_layout()
            wandb_run.log(
                {f"white noise analysis {target_block} - {im}": fig},
            )
            plt.close(fig)


def generate_white_noise_analysis(model, target_block, shape, n_samples=100, sigma=0.6):
    import scipy

    white_noise = np.random.normal(size=(n_samples, np.prod(shape)),
                                   loc=0.0, scale=1.).astype(np.float32)

    # apply ndimage.gaussian_filter with sigma=0.6
    for i in range(n_samples):
        white_noise[i, :] = scipy.ndimage.gaussian_filter(
            white_noise[i, :].reshape(shape), sigma=sigma).reshape(np.prod(shape))

    with torch.no_grad():
        computed, _ = model(torch.ones(1, *shape, device=params.device), stop_at=target_block)
        target_block_dim = computed[target_block].shape[1:]
        target_block_values = torch.zeros((n_samples, *target_block_dim), device=params.device)

        # loop over a batch of 128 white_noise images
        batch_size = params.analysis_params.batch_size
        for i in range(0, n_samples, batch_size):
            batch = white_noise[i:i+batch_size, :].reshape(-1, *shape)
            computed_target, _ = model(torch.tensor(batch, device=params.device),
                                       use_mean=True, stop_at=target_block)
            target_block_values[i:i+batch_size] = computed_target[target_block]

        target_block_values = torch.flatten(target_block_values, start_dim=1)
        # multiply transpose of target block_values with white noise tensorially
        receptive_fields = torch.matmul(
            target_block_values.T, torch.tensor(white_noise, device=params.device)
        ) / np.sqrt(n_samples)
        return receptive_fields.detach().cpu().numpy()


def decodability(model, labeled_loader, wandb_run, logger: logging.Logger):
    logger.info('Computing Decodability')
    results = calculate_decodability(model, labeled_loader)
    accuracies = {decode_from: accuracy for decode_from, (_, accuracy) in results.items()}
    for decode_from, (loss_history, accuracy) in results.items():
        # loss history -> line plot
        data = [[x, y] for (x, y) in enumerate(loss_history)]
        table = wandb.Table(data=data, columns=["step", "loss"])
        wandb_run.log({"decodability_loss_history":
                      wandb.plot.line(table, "step", "loss",
                                      title=f"Decodability Loss History {decode_from}")})

    # accuracy -> bar plot
    data = [[decode_from, acc] for (decode_from, acc) in accuracies.items()]
    table = wandb.Table(data=data, columns =["decode_from", "accuracy"])
    wandb_run.log({"decodability_accuracies":
                   wandb.plot.bar(table, "decode_from", "accuracy",
                                  title="Deocdability Accuracies")})
    logger.info(f'Decodability calculation successful')


def calculate_decodability(model, labeled_loader):
    from .elements.dataset import FunctionalDataset

    decode_from_list = params.analysis_params.decodability.keys()
    X = {layer: [] for layer in decode_from_list}
    Y = []
    for batch in labeled_loader:
        inputs, labels = batch
        computed, _ = model(inputs, use_mean=True)
        for decode_from in decode_from_list:
            X[decode_from].append(
                computed[decode_from].numpy())
            Y.append(labels)
    X = {block: np.concatenate(block_inputs, axis=0)
         for block, block_inputs in X.items()}
    Y = np.concatenate(Y, axis=0)

    results = dict()
    for decode_from in decode_from_list:
        decoder_model = params.analysis_params.decodability[decode_from]["model"]()
        decoding_dataset = FunctionalDataset(data=X[decode_from], labels=Y)
        optimizer = params.analysis_params.decodability[decode_from]["optimizer"](
            decoder_model.parameters(),
            lr=params.analysis_params.decodability[decode_from]["learning_rate"])
        loss = params.analysis_params.decodability[decode_from]["loss"]()
        loss_history, accuracy = train_decoder(
            decoder_model, optimizer, loss, params.analysis_params.decodability[decode_from]["epochs"],
            params.analysis_params.decodability[decode_from]["batch_size"], decoding_dataset)
        results[decode_from] = (loss_history, accuracy)
    return results


def train_decoder(decoder_model, optimizer, loss, epochs, batch_size, dataset):
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    loss_history = []
    # train model
    for epoch in range(epochs):
        for batch in dataloader:
            X, Y = batch
            optimizer.zero_grad()
            output = decoder_model(X)
            batch_loss = loss(output, Y)
            loss_history.append(batch_loss.item())
            batch_loss.backward()
            optimizer.step()

    # evaluate model
    # TODO: add evaluation -> calcualte accuracy
    return loss_history, 0


def latent_step_analysis(model, dataloader, wandb_run, logger: logging.Logger):
    logger.info('Generating Samples with Latent Step Analysis')
    sample = next(iter(dataloader))
    shape = sample.shape[1:]
    for target_block, config in params.analysis_params.latent_step_analysis.items():
        receptive_fields = generate_latent_step_analysis(model, sample, target_block, **config)
        n_dims = len(receptive_fields)
        dims_per_image = np.prod(shape[-2:]) // 20
        n_images = n_dims // dims_per_image + 1

        for im in range(n_images):
            n_dims_im = min(dims_per_image, n_dims - im * dims_per_image)
            start_dim = im * dims_per_image
            n_rows = math.ceil(n_dims_im / 20)
            w = int(shape[-2])
            h = int(shape[-1] / 20 * n_rows)

            fig = figure(figsize=(w, h))
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
            for i in range(n_dims_im):
                ax = fig.add_subplot(n_rows, 20, i + 1)
                ax.imshow(receptive_fields[start_dim + i].reshape(params.data_params.shape[-2:]), cmap="gray")
                ax.set_title(f"dim {i}")
                ax.axis("off")

            wandb_run.log(
                {f"latent step analysis {target_block}": fig},
            )
            plt.close(fig)
    logger.info('Latent Step Analysis Successful Images')


def generate_latent_step_analysis(model, sample, target_block, diff=1, value=1):
    def copy_computed(computed):
        return {k: v.clone() for k, v in computed.items()}

    with torch.no_grad():
        target_computed, _ = model(sample.to(params.device), use_mean=True, stop_at=target_block)
        input_0 = target_computed[target_block]
        shape = input_0.shape
        n_dims = np.prod(shape[1:])

        computed_checkpoint = copy_computed(target_computed)
        output_computed, _ = model(computed_checkpoint, use_mean=True)
        output_0 = torch.mean(output_computed['output'], dim=0)

        visualizations = []
        for i in range(n_dims):
            input_i = torch.zeros([1, n_dims], device=params.device)
            input_i[0, i] = value
            input_i = input_i.reshape(shape[1:])
            input_i = input_0 + input_i
            target_computed[target_block] = input_i

            computed_checkpoint = copy_computed(target_computed)
            trav_output_computed, _ = model(computed_checkpoint, use_mean=True)
            output_i = torch.mean(trav_output_computed['output'], dim=0)

            latent_step_vis = output_i - diff * output_0
            visualizations.append(latent_step_vis.detach().cpu().numpy())

        return visualizations





