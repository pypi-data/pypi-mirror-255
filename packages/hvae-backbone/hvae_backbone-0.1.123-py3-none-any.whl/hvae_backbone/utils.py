import os
import logging
import json
import pickle
import numpy as np
import torch
import wandb
from torch.nn import Sequential, Module, ModuleList

"""
-------------------
MODEL UTILS
-------------------
"""


class OrderedModuleDict(torch.nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        self._keys = list()
        self._values = ModuleList([])
        for key, module in kwargs.items():
            self[key] = module

    def update(self, modules):
        for key, module in modules.items():
            self[key] = module

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        elif isinstance(key, str):
            index = self._keys.index(key)
            return self._values[index]
        else:
            raise KeyError(f"Key {key} is not a string or an integer")

    def __setitem__(self, key, module):
        if key in self._keys:
            raise KeyError(f"Key {key} already exists")
        self._keys.append(key)
        self._values.append(module)

    def __len__(self):
        return len(self.keys())

    def __iter__(self):
        return iter(self._values)

    def keys(self):
        return self._keys

    def values(self):
        return self._values


def scale_pixels(img, data_num_bits):
    img = np.floor(img / np.uint8(2 ** (8 - data_num_bits))) * 2 ** (8 - data_num_bits)
    shift = scale = (2 ** 8 - 1) / 2
    img = (img - shift) / scale  # Images are between [-1, 1]
    return img


def shuffle_along_axis(a, axis):
    idx = np.random.rand(*a.shape).argsort(axis=axis)
    return np.take_along_axis(a, idx, axis=axis)


def get_same_padding(kernel_size, strides, dilation_rate, n_dims=2):
    p_ = []
    # Reverse order for F.pad
    for i in range(n_dims - 1, -1, -1):
        if strides[i] > 1 and dilation_rate[i] > 1:
            raise ValueError("Can't have the stride and dilation rate over 1")
        p = (kernel_size[i] - strides[i]) * dilation_rate[i]
        if p % 2 == 0:
            p = (p // 2, p // 2)
        else:
            p = (int(np.ceil(p / 2)), int(np.floor(p / 2)))

        p_ += p

    return tuple(p_)


def get_valid_padding(n_dims=2):
    p_ = (0,) * 2 * n_dims
    return p_


def get_causal_padding(kernel_size, strides, dilation_rate, n_dims=2):
    p_ = []
    for i in range(n_dims - 1, -1, -1):
        if strides[i] > 1 and dilation_rate[i] > 1:
            raise ValueError("can't have the stride and dilation over 1")
        p = (kernel_size[i] - strides[i]) * dilation_rate[i]

        p_ += (p, 0)

    return p_


def get_variate_masks(stats, quantile=0.03):
    thresh = np.quantile(stats, 1 - quantile)
    variate_masks = stats > thresh
    return variate_masks


def linear_temperature(min_temp, max_temp, n_layers):
    slope = (max_temp - min_temp) / n_layers

    def get_layer_temp(layer_i):
        return slope * layer_i + min_temp

    return get_layer_temp


def split_mu_sigma(x, chunks=2, dim=1):
    if x.shape[dim] % chunks != 0:
        if x.shape[dim] == 1:
            return x, None
        """
        raise ValueError(f"Can't split tensor of shape "
                         f"{x.shape} into {chunks} chunks "
                         f"along dim {dim}")"""
    chunks = torch.chunk(x, chunks, dim=dim)
    if chunks[0].shape[dim] == 1:
        for chunk in chunks:
            chunk.squeeze(dim=dim)
    return chunks


"""
-------------------
TRAIN/LOG UTILS
-------------------
"""


def load_model(load_from, run=None):
    from .checkpoint import Checkpoint

    assert load_from is not None
    experiment = None

    if os.path.exists(load_from):
        load_from_file = load_from
    else:
        wandb_dir = wandb_load_checkpoint(load_from, run)
        load_from_file = os.path.join(wandb_dir, "model.pth")

    # load experiment from checkpoint
    if load_from_file is not None and os.path.isfile(load_from_file):
        # print(f"Loading experiment from {load_from_file}")
        experiment = Checkpoint.load(load_from_file)
    return experiment


def load_experiment_for(mode='train', run=None, log_params=None):
    if mode == 'train':
        if log_params.load_from_train is None:
            checkpoint = None
        else:
            checkpoint = load_model(log_params.load_from_train, run)
        import datetime
        save_dir = f"experiments/{log_params.name}/{datetime.datetime.now().strftime('%Y-%m-%d__%H-%M')}"
        os.makedirs(save_dir, exist_ok=True)
        return checkpoint, save_dir

    elif mode == 'migration':
        import datetime
        save_dir = f"experiments/{log_params.name}/{datetime.datetime.now().strftime('%Y-%m-%d__%H-%M')}"
        os.makedirs(save_dir, exist_ok=True)
        return None, save_dir

    elif mode == 'test':
        checkpoint = load_model(log_params.load_from_eval, run)
        return checkpoint, None
    else:
        raise ValueError(f"Unknown mode {mode}")


def setup_logger(checkpoint_path: str) -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('logger')
    if checkpoint_path is not None:
        file_handler = logging.FileHandler(os.path.join(checkpoint_path, 'log.txt'))
        logger.addHandler(file_handler)
    return logger


def prepare_for_log(results: dict):
    results = {k: (v.detach().cpu().item()
                   if isinstance(v, torch.Tensor)
                   else prepare_for_log(v) if isinstance(v, dict)
    else v)
               for k, v in results.items() if v is not None}
    return results


def params_to_file(params, filepath):
    extension = filepath.split('.')[-1]
    if extension == "txt":
        with open(filepath, 'a') as file:
            text = "PARAMETERS\n"
            for param_group in params.keys():
                text += f"{param_group}:\n" \
                        f"-------------------\n"
                for param in params[param_group].keys():
                    text += f"{param}: {params[param_group][param]}\n"
                text += f"-------------------\n"
            file.write(text)
            file.close()
    elif extension == "json":
        import json
        with open(filepath, 'w') as file:
            json.dump(params.to_json(), file, indent=4)
            file.close()
    return True


def log_to_csv(results, checkpoint_path, mode: str = 'train'):
    import pandas as pd
    filepath = os.path.join(checkpoint_path, f'{mode}_log.csv')
    new_record = pd.DataFrame(results, index=[0])
    if os.path.isfile(filepath):
        df = pd.read_csv(filepath)
        df = pd.concat([df, new_record], ignore_index=True)
    else:
        df = new_record
    df.to_csv(filepath, index=False)


def print_line(logger: logging.Logger, newline_after: False):
    logger.info('\n' + '-' * 89 + ('\n' if newline_after else ''))


def wandb_init(name, config, job_type=None):
    import wandb
    run = wandb.init(
        project=name,
        config=config,
        job_type=job_type
    )
    return run


def wandb_log_results(run, results, global_step=None, mode='Train'):
    results = {f"{mode}/{k}": v if not isinstance(v, dict)
                              else wandb.plot.line_series(xs=list(range(len(v))),
                                                          ys=v.values(),
                                                          keys=v.keys(),
                                                          title="KL Divergence Statistics",
                                                          xname="timestep")
               for k, v in results.items()}
    run.log(results, step=global_step)


def wandb_log_checkpoint(run, path, name):
    artifact = wandb.Artifact(name, type='model')
    artifact.add_file(path)
    run.log_artifact(artifact)


def wandb_load_checkpoint(path, run=None):
    if run is None:
        api = wandb.Api()
        artifact = api.artifact(path, type="model")
    else:
        artifact = run.use_artifact(path, type="model")
    artifact_dir = artifact.download(
        root=f"./wandb/artifacts/{artifact.name}"
    )
    return artifact_dir


"""
-------------------
SERIALIZATION UTILS
-------------------
"""


class SerializableModule(Module):

    def __init__(self, *args):
        super().__init__()

    def serialize(self):
        return dict(type=self.__class__)

    @staticmethod
    def deserialize(serialized):
        return serialized["type"]


class SerializableSequential(Sequential, SerializableModule):

    def __init__(self, *args):
        super().__init__(*args)

    def serialize(self):
        serialized = dict(
            type=self.__class__,
            params=[layer.serialize() for layer in self._modules.values()]
        )
        return serialized

    @staticmethod
    def deserialize(serialized):
        for layer in serialized["params"]:
            if not isinstance(layer, dict):
                print(layer)
        sequential = SerializableSequential(*[
            layer["type"].deserialize(layer)
            for layer in serialized["params"]
        ])
        return sequential


class SharedSerializableSequential(SerializableSequential):
    def __init__(self, _id):
        super().__init__()
        # generate random id
        if _id is None:
            self.id = np.random.randint(0, 1000000)
        else:
            self.id = _id

    def serialize(self):
        return dict(type=self.__class__, params=dict(id=self.id))

    @staticmethod
    def deserialize(serialized):
        return serialized["type"](serialized["params"]["id"])


def handle_shared_modules(module, shared_nets):
    for net in module.children():
        if isinstance(net, SharedSerializableSequential):
            if net.id not in shared_nets.keys():
                shared_nets[net.id] = net
            else:
                net.parameters = shared_nets.pop(net.id).parameters
    return module, shared_nets


def unpickle(file):
    with open(file, 'rb') as fo:
        _dict = pickle.load(fo)
    return _dict
