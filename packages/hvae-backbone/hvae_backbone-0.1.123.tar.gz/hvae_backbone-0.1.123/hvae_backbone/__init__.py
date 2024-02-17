import numpy as np
import torch
from . import utils

params = None


def init_globals(config):
    global params
    params = config
    params.device = params.model_params.device

    from .elements.losses import StructureSimilarityIndexMap, get_reconstruction_loss, get_kl_loss
    from .elements.schedules import get_beta_schedule, get_gamma_schedule

    params.reconstruction_loss = get_reconstruction_loss()
    params.kl_divergence =  get_kl_loss()
    params.kldiv_schedule = get_beta_schedule()
    params.gamma_schedule = get_gamma_schedule()
    params.ssim_metric =    StructureSimilarityIndexMap(image_channels=params.data_params.shape[0])
    return params


def training(config):
    p = init_globals(config)

    wandb = utils.wandb_init(name=p.log_params.name, config=p.to_json(), job_type='train')
    checkpoint, checkpoint_path = utils.load_experiment_for('train', wandb, p.log_params)
    logger = utils.setup_logger(checkpoint_path)
    device = p.model_params.device

    if checkpoint is not None:
        gloabal_step = checkpoint.global_step
        model = checkpoint.get_model()
        logger.info(f'Loaded Model Checkpoint from {p.log_params.load_from_train}')
    else:
        gloabal_step = -1
        model = p.model_params.model()

    model.summary()
    model_parameters = filter(lambda param: param.requires_grad, model.parameters())
    logger.info(f'Number of trainable params '
                f'{np.sum([np.prod(v.size()) for v in model_parameters]) / 1000000:.3f}m.')
    model = model.to(device)

    from .elements.optimizers import get_optimizer
    from .elements.schedules import get_schedule
    optimizer = get_optimizer(model=model,
                              type=p.optimizer_params.type,
                              learning_rate=p.optimizer_params.learning_rate,
                              beta_1=p.optimizer_params.beta1,
                              beta_2=p.optimizer_params.beta2,
                              epsilon=p.optimizer_params.epsilon,
                              weight_decay_rate=p.optimizer_params.l2_weight,
                              checkpoint=checkpoint)
    schedule = get_schedule(optimizer=optimizer,
                            decay_scheme=p.optimizer_params.learning_rate_scheme,
                            warmup_steps=p.optimizer_params.warmup_steps,
                            decay_steps=p.optimizer_params.decay_steps,
                            decay_rate=p.optimizer_params.decay_rate,
                            decay_start=p.optimizer_params.decay_start,
                            min_lr=p.optimizer_params.min_learning_rate,
                            last_epoch=torch.tensor(gloabal_step),
                            checkpoint=checkpoint)

    dataset = p.data_params.dataset(**p.data_params.params)
    train_loader = dataset.get_train_loader(p.train_params.batch_size)
    val_loader = dataset.get_val_loader(p.eval_params.batch_size)

    if p.train_params.unfreeze_first:
        model.unfreeeze()
    if len(p.train_params.freeze_nets) > 0:
        model.freeze(p.train_params.freeze_nets)

    from .functional import train
    train(model, optimizer, schedule, train_loader, val_loader, gloabal_step, wandb, checkpoint_path, logger)
    wandb.finish()


def testing(config):
    p = init_globals(config)

    wandb = utils.wandb_init(name=p.log_params.name, config=p.to_json(), job_type='test')
    checkpoint, checkpoint_path = utils.load_experiment_for('test', wandb, p.log_params)
    device = p.model_params.device

    assert checkpoint is not None
    model = checkpoint.get_model()
    print(f'Model Checkpoint is loaded from {p.log_params.load_from_eval}')

    model.summary()
    model = model.to(device)

    dataset = p.data_params.dataset(**p.data_params.params)
    test_loader = dataset.get_test_loader(p.eval_params.batch_size)

    from .functional import reconstruct
    reconstruct(
        net=model,
        dataset=test_loader,
        wandb_run=wandb,
        use_mean=p.eval_params.use_mean
    )
    wandb.finish()


def migrate(config):
    p = init_globals(config)

    _, save_path = utils.load_experiment_for('migration', log_params=p.log_params)
    m = p.migration_params

    migration = m.migration_agent(**m.params)

    model = p.model_params.model(migration).cpu()
    global_step = migration.get_global_step()

    model.summary()

    from .elements.optimizers import get_optimizer
    from .elements.schedules import get_schedule
    optimizer = get_optimizer(model=model,
                              type=p.optimizer_params.type,
                              learning_rate=p.optimizer_params.learning_rate,
                              beta_1=p.optimizer_params.beta1,
                              beta_2=p.optimizer_params.beta2,
                              epsilon=p.optimizer_params.epsilon,
                              weight_decay_rate=p.optimizer_params.l2_weight,
                              checkpoint=migration.get_optimizer())
    schedule = get_schedule(optimizer=optimizer,
                            decay_scheme=p.optimizer_params.learning_rate_scheme,
                            warmup_steps=p.optimizer_params.warmup_steps,
                            decay_steps=p.optimizer_params.decay_steps,
                            decay_rate=p.optimizer_params.decay_rate,
                            decay_start=p.optimizer_params.decay_start,
                            min_lr=p.optimizer_params.min_learning_rate,
                            last_epoch=torch.tensor(-1),
                            checkpoint=migration.get_schedule())

    from .checkpoint import Checkpoint

    checkpoint = Checkpoint(
        global_step=global_step,
        model=model,
        optimizer=optimizer,
        scheduler=schedule
    )
    checkpoint.save_migration(save_path)


def analysis(config):
    p = init_globals(config)

    wandb = utils.wandb_init(name=p.log_params.name, config=p.to_json(), job_type='analysis')
    checkpoint, save_path = utils.load_experiment_for('test', wandb, log_params=p.log_params)
    logger = utils.setup_logger(save_path)

    assert checkpoint is not None
    model = checkpoint.get_model()
    logger.info(f'Model Checkpoint is loaded from {p.log_params.load_from_eval}')

    model.summary()
    model = model.to(p.model_params.device)
    dataset = p.data_params.dataset(**p.data_params.params)

    from .analysis import generation, mei, white_noise_analysis, \
        decodability, latent_step_analysis, extrapolate
    for operation in p.analysis_params.ops:
        if operation == 'generation':
            generation(model, wandb, logger)
        elif operation == 'mei':
            mei(model, wandb, logger)
        elif operation == 'white_noise_analysis':
            white_noise_analysis(model, wandb, logger)
        elif operation == 'decodability':
            decodability(model, dataset, wandb, logger)
        elif operation == 'latent_step_analysis':
            dataloader = dataset.get_val_loader(p.analysis_params.batch_size)
            latent_step_analysis(model, dataloader, wandb, logger)
        elif operation == 'extrapolate':
            from .sequence import hSequenceVAE
            assert isinstance(model, hSequenceVAE)
            dataloader = dataset.get_val_loader(p.analysis_params.batch_size)
            extrapolate(model, dataloader, wandb, logger)
        else:
            logger.error(f'Unknown Mode {operation}')
            raise ValueError(f'Unknown Mode {operation}')
    logger.info(f'Analysis tasks performed successfully')
    wandb.finish()


class Hyperparams:
    def __init__(self, **config):
        self.config = config

    def __getattr__(self, name):
        if name == 'config':
            return super().__getattribute__(name)
        return self.config[name]

    def __setattr__(self, name, value):
        if name == 'config':
            super().__setattr__(name, value)
        else:
            self.config[name] = value

    def __getstate__(self):
        return self.config

    def __setstate__(self, state):
        self.config = state

    def keys(self):
        return self.config.keys()

    def __getitem__(self, item):
        return self.config[item]

    def to_json(self):
        from types import FunctionType
        from .elements.dataset import DataSet

        def convert_to_json_serializable(obj):
            if isinstance(obj, Hyperparams):
                return convert_to_json_serializable(obj.config)
            if isinstance(obj, (list, tuple)):
                return [convert_to_json_serializable(item) for item in obj]
            if isinstance(obj, dict):
                return {key: convert_to_json_serializable(value) for key, value in obj.items()}
            if callable(obj) or isinstance(obj, FunctionType):
                return str(obj)
            if isinstance(obj, DataSet):
                return str(obj)
            return obj

        json_serializable_config = convert_to_json_serializable(self.config)
        return json_serializable_config

    @classmethod
    def from_json(cls, json_str):
        import json
        data = json.loads(json_str)
        return cls(**data)

    @staticmethod
    def from_dict(dictionary):
        return Hyperparams(**{k: Hyperparams.from_dict(v) if isinstance(v, dict) else v
                              for k, v in dictionary.items()})


def load_model(path, loaded_params, wandb_run=False):
    if not wandb_run:
        checkpoint = utils.load_model(path)
        init_globals(loaded_params)
        return checkpoint.model
    else:
        raise NotImplementedError()
        wandb_run = utils.wandb_init(name='test', config={})
        checkpoint = utils.load_model(path, wandb_run)
        init_globals(loaded_params)
        return checkpoint.model, wandb_run
