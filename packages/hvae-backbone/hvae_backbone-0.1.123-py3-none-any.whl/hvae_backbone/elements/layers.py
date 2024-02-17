import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.init as init
import numpy as np

from .distributions import generate_distribution
from ..utils import SerializableModule, get_same_padding, get_valid_padding, get_causal_padding, split_mu_sigma

"""
Layers are modifications of the ones used in Efficient-VDVAE paper
"""


class Interpolate(SerializableModule):
    def __init__(self, scale_factor, mode='nearest'):
        super(Interpolate, self).__init__()
        self.scale_factor = scale_factor
        self.mode = mode

    def forward(self, x):
        return F.interpolate(x, scale_factor=self.scale_factor, mode=self.mode)

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            scale_factor=self.scale_factor,
            mode=self.mode
        )
        return serialized

    @staticmethod
    def deserialize(serialized):
        return Interpolate(**serialized["params"])


class UnPooLayer(SerializableModule):
    def __init__(self, in_filters, filters, strides, activation=None):
        super(UnPooLayer, self).__init__()
        self.in_filters = in_filters
        self.filters = filters

        self.activation = activation if activation is not None \
            else nn.LeakyReLU(negative_slope=0.1)

        if isinstance(strides, int):
            self.strides = (strides, strides)
        else:
            self.strides = strides

        ops = [nn.UpsamplingNearest2d(scale_factor=self.strides),
               Conv2d(in_channels=in_filters, out_channels=filters,
                      kernel_size=(1, 1), stride=(1, 1), padding='same'),
               nn.BatchNorm2d(filters),
               self.activation]

        self.ops = nn.Sequential(*ops)


    def forward(self, x):
        x = self.ops(x)
        return x

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            in_filters=self.in_filters,
            filters=self.filters,
            strides=self.strides
        )
        serialized["state_dict"] = self.state_dict()
        return serialized

    @staticmethod
    def deserialize(serialized):
        layer = UnPooLayer(**serialized["params"])
        layer.load_state_dict(serialized["state_dict"])
        return layer

    @staticmethod
    def from_hparams(hparams):
        return UnPooLayer(
            in_filters=hparams.in_filters,
            filters=hparams.filters,
            strides=hparams.strides
        )


class PoolLayer(SerializableModule):
    def __init__(self, in_filters, filters, strides, activation=None):
        super(PoolLayer, self).__init__()
        self.in_filters = in_filters
        self.filters = filters
        self.strides = strides

        self.activation = activation if activation is not None \
            else nn.LeakyReLU(negative_slope=0.1)

        if isinstance(strides, int):
            strides = (strides, strides)

        ops = [Conv2d(in_channels=in_filters, out_channels=filters,
                      kernel_size=strides, stride=strides, padding='same'),
               nn.BatchNorm2d(filters),
               self.activation]

        self.ops = nn.Sequential(*ops)

    def forward(self, x):
        x = self.ops(x)
        return x

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            in_filters=self.in_filters,
            filters=self.filters,
            strides=self.strides
        )
        serialized["state_dict"] = self.state_dict()
        return serialized

    @staticmethod
    def deserialize(serialized):
        layer = PoolLayer(**serialized["params"])
        layer.load_state_dict(serialized["state_dict"])
        return layer

    @staticmethod
    def from_hparams(hparams):
        return PoolLayer(
            in_filters=hparams.in_filters,
            filters=hparams.filters,
            strides=hparams.strides
        )


class FixedStdDev(SerializableModule):
    def __init__(self, std):
        super(FixedStdDev, self).__init__()
        self.std = std

    def forward(self, x):
        return torch.concatenate([x, self.std * torch.ones_like(x)], dim=1)

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            std=self.std
        )
        return serialized

    @staticmethod
    def deserialize(serialized):
        return FixedStdDev(**serialized["params"])


class Slice(SerializableModule):
    def __init__(self, slice_indices):
        super(Slice, self).__init__()
        self.slice = slice_indices if isinstance(slice_indices, slice) \
            else slice(*slice_indices)

    def forward(self, x):
        return x[:, self.slice]

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            slice=self.slice
        )
        return serialized

    @staticmethod
    def deserialize(serialized):
        slice_indices = serialized["params"]["slice"]
        return Slice(slice_indices)


class KeepShapeWithValue(SerializableModule):
    def __init__(self, value):
        super(KeepShapeWithValue, self).__init__()
        self.value = value

    def forward(self, x):
        return self.value * torch.ones_like(x)

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            value=self.value
        )
        return serialized

    @staticmethod
    def deserialize(serialized):
        return KeepShapeWithValue(**serialized["params"])


class EinsumLayer(SerializableModule):
    def __init__(self, equation):
        super(EinsumLayer, self).__init__()
        self.equation = equation

    def forward(self, inputs):
        output = torch.einsum(self.equation, inputs)
        return output

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            equation=self.equation
        )
        return serialized

    @staticmethod
    def deserialize(serialized):
        return EinsumLayer(**serialized["params"])


class Conv2d(nn.Conv2d, SerializableModule):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding='same', dilation=1):
        if isinstance(kernel_size, int):
            kernel_size = (kernel_size,) * 2
        if isinstance(stride, int):
            stride = (stride,) * 2
        if isinstance(dilation, int):
            dilation = (dilation,) * 2

        self.stride = stride

        self.padding_str = padding.upper()
        if self.padding_str == 'SAME':
            self.pad_values = get_same_padding(kernel_size, stride, dilation)

        elif self.padding_str == 'VALID':
            self.pad_values = get_valid_padding()

        elif self.padding_str == 'CAUSAL':
            self.pad_values = get_causal_padding(kernel_size, stride, dilation)

        else:
            raise ValueError

        self.condition = np.sum(self.pad_values) != 0

        super().__init__(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=0,
            dilation=dilation
        )

    def forward(self, x):
        if self.condition:
            x = F.pad(x, self.pad_values)
        x = super().forward(x)
        return x

    def reset_parameters(self) -> None:
        init.xavier_uniform_(self.weight)
        if self.bias is not None:
            init.zeros_(self.bias)

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            in_channels=self.in_channels,
            out_channels=self.out_channels,
            kernel_size=self.kernel_size,
            stride=self.stride,
            padding=self.padding,
            dilation=self.dilation
        )
        return serialized

    @staticmethod
    def deserialize(serialized):
        return Conv2d(**serialized["params"])


class Flatten(torch.nn.Flatten, SerializableModule):
    def __init__(self, start_dim=1, end_dim=-1):
        super(Flatten, self).__init__(start_dim=start_dim, end_dim=end_dim)

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            start_dim=self.start_dim,
            end_dim=self.end_dim
        )
        return serialized

    @staticmethod
    def deserialize(serialized):
        return Flatten(**serialized["params"])


class Unflatten(torch.nn.Unflatten, SerializableModule):
    def __init__(self, dim, unflattened_size):
        super(Unflatten, self).__init__(dim, unflattened_size)
        self.unflattened_size = unflattened_size
        self.dim = dim

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            dim=self.dim,
            unflattened_size=self.unflattened_size
        )
        return serialized

    @staticmethod
    def deserialize(serialized):
        return Unflatten(**serialized["params"])


class RandomScaler(SerializableModule):

    def __init__(self):
        super(RandomScaler, self).__init__()

    def forward(self, x):
        return x * torch.randn((1,))

    def serialize(self):
        serialized = super().serialize()
        return serialized

    @staticmethod
    def deserialize(serialized):
        return RandomScaler()


class SpatialBroadcast(SerializableModule):
    def __init__(self, target_shape):
        super(SpatialBroadcast, self).__init__()

        assert len(target_shape) == 2, "Broadcast shape must be (h, w)"
        self.shape = target_shape  # (h, w)

        a = np.linspace(-1, 1, self.shape[0])
        b = np.linspace(-1, 1, self.shape[1])
        x, y = np.meshgrid(a, b)
        x = x[np.newaxis, :, :]
        y = y[np.newaxis, :, :]
        self.xy = np.concatenate((x, y), axis=0)

    def forward(self, z):
        batch_size = z.shape[0]
        c = z.shape[1]
        if len(z.shape) == 4:
            h = z.shape[2]
            w = z.shape[3]
        elif len(z.shape) == 2:
            h = 1
            w = 1
        else:
            raise ValueError(f"Expected 2 or 4 dimensional input, got {z.shape}")

        xy_tiled = torch.from_numpy(
            np.tile(self.xy, (batch_size, 1, 1, 1)).astype(np.float32)).to(z.device)

        n_tiles = int(self.shape[0] / h * self.shape[1] / w)
        z_tiled = z.repeat_interleave(n_tiles, dim=0)\
            .view(batch_size, c, *self.shape)
        z_and_xy = torch.cat((z_tiled, xy_tiled), dim=1)

        return z_and_xy

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            shape=self.shape
        )
        return serialized

    @staticmethod
    def deserialize(serialized):
        return SpatialBroadcast(**serialized["params"])


class PixelShuffle(SerializableModule):
    def __init__(self, upscale_factor):
        super(PixelShuffle, self).__init__()
        self.upscale_factor = upscale_factor

    def forward(self, x):
        return F.pixel_shuffle(x, self.upscale_factor)

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            upscale_factor=self.upscale_factor
        )
        return serialized

    @staticmethod
    def deserialize(serialized):
        return PixelShuffle(**serialized["params"])


class Sample(SerializableModule):

    def __init__(self, distribution):
        self.distribution = distribution
        super(Sample, self).__init__()

    def forward(self, x):
        mu, sigma = split_mu_sigma(x)
        dist = generate_distribution(mu, sigma, self.distribution)
        return dist.rsample()

    def serialize(self):
        serialized = super().serialize()
        serialized["params"] = dict(
            distribution=self.distribution
        )
        return serialized

    @staticmethod
    def deserialize(serialized):
        return Sample(**serialized["params"])



