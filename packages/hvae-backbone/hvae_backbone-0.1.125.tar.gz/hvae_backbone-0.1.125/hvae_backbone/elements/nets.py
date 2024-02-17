from collections import OrderedDict
from torch import tensor
from torch.nn import init

from ..elements.layers import *
from ..utils import SerializableModule, SerializableSequential as Sequential
from .. import Hyperparams


def get_net(model):
    """
    Get net from
    -string model type,
    -hyperparameter config
    -SerializableModule or SerializableSequential object
    -or list of the above

    :param model: str, Hyperparams, SerializableModule, SerializableSequential, list
    :return: SerializableSequential
    """

    if model is None:
        return Sequential()

    # Load model from hyperparameter config
    elif isinstance(model, Hyperparams):

        if "type" not in model.keys():
            raise ValueError("Model type not specified.")
        if model.type == 'mlp':
            return MLPNet.from_hparams(model)
        elif model.type == 'conv':
            return ConvNet.from_hparams(model)
        elif model.type == 'deconv':
            return DeconvNet.from_hparams(model)
        else:
            raise NotImplementedError("Model type not supported.")

    elif isinstance(model, BlockNet):
        return model

    # Load model from SerializableModule
    elif isinstance(model, SerializableModule):
        return model

    # Load model from SerializableSequential
    elif isinstance(model, Sequential):
        return model

    # Load model from list of any of the above
    elif isinstance(model, list):
        # Load model from list
        return Sequential(*list(map(get_net, model)))

    else:
        raise NotImplementedError("Model type not supported.")


class MLPNet(SerializableModule):

    """
    Parametric multilayer perceptron network

    :param input_size: int, the size of the input
    :param hidden_sizes: list of int, the sizes of the hidden layers
    :param output_size: int, the size of the output
    :param residual: bool, whether to use residual connections
    :param activation: torch.nn.Module, the activation function to use
    """
    def __init__(self, input_size, hidden_sizes, output_size, residual=False, activation=nn.ReLU(), activate_output=True):
        super(MLPNet, self).__init__()
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size
        self.activation = activation
        self.residual = residual
        self.activate_output = activate_output

        layers = []
        sizes = [input_size] + hidden_sizes + [output_size]
        for i in range(len(sizes) - 1):
            layers.append(nn.Linear(sizes[i], sizes[i + 1]))
            if i < len(sizes) - 2 or self.activate_output:
                layers.append(self.activation)

        self.mlp_layers = nn.Sequential(*layers)

    def forward(self, inputs):
        x = inputs
        x = self.mlp_layers(x)
        outputs = x if not self.residual else inputs + x
        return outputs


    @staticmethod
    def from_hparams(hparams: Hyperparams):
        return MLPNet(
            input_size=hparams.input_size,
            hidden_sizes=hparams.hidden_sizes,
            output_size=hparams.output_size,
            activation=hparams.activation,
            residual=hparams.residual,
            activate_output=hparams.activate_output
        )

    def serialize(self):
        return dict(
            type=self.__class__,
            state_dict=self.state_dict(),
            params=dict(
                input_size=self.input_size,
                hidden_sizes=self.hidden_sizes,
                output_size=self.output_size,
                activation=self.activation,
                residual=self.residual,
                activate_output=self.activate_output
            )
        )

    @staticmethod
    def deserialize(serialized):
        net = MLPNet(**serialized["params"])
        net.load_state_dict(serialized["state_dict"])
        return net


class ConvNet(SerializableModule):
    """
    Parametric convolutional network
    based on Efficient-VDVAE paper

    :param in_filters: int, the number of input filters
    :param filters: list of int, the number of filters for each layer
    :param kernel_size: int or tuple of int, the size of the convolutional kernel
    :param pool_strides: int or tuple of int, the strides for the pooling layers
    :param unpool_strides: int or tuple of int, the strides for the unpooling layers
    :param activation: torch.nn.Module, the activation function to use
    """
    def __init__(self, in_filters, filters, kernel_size, pools=None,
                 activation=nn.Softplus(), activate_output=False,
                 batchnorm=None, init=None):
        super(ConvNet, self).__init__()

        self.in_filters = in_filters
        self.filters = filters
        assert len(self.filters) > 0, "Must have at least one filter"

        if isinstance(kernel_size, int):
            kernel_size = [(kernel_size, kernel_size)
                           for _ in range(len(self.filters))]
        elif isinstance(kernel_size, list):
            kernel_size = [(ks, ks) if isinstance(ks, int) else ks
                           for ks in kernel_size]
        self.kernel_size = kernel_size

        if pools is None:
            pools = []
        self.pools = pools
        self.activation = activation
        self.activate_output = activate_output
        self.batchnorm: bool = batchnorm

        def stride_padding_kernel(i: int):
            kernel = self.kernel_size[i]
            if i in self.pools:
                padding1 = (kernel[0] - 1) // 2
                padding2 = (kernel[1] - 1) // 2
                padding = (padding1, padding2)
                stride = 2
            else:
                padding = "same"
                stride = 1
            return dict(stride=stride, padding=padding, kernel_size=kernel)

        i = 0
        convs = nn.Sequential(
            nn.Conv2d(in_channels=self.in_filters,
                      out_channels=self.filters[0],
                      **stride_padding_kernel(i)),
        )
        for i in range(len(self.filters)-1):
            if self.batchnorm:
                nn.BatchNorm2d(self.filters[i]),
            convs.append(self.activation)
            convs.append(nn.Conv2d(in_channels=self.filters[i],
                                   out_channels=self.filters[i + 1],
                                   **stride_padding_kernel(i+1)))
        if self.activate_output:
            convs.append(self.activation)

        self.convs = nn.Sequential(*convs)
        self.init = init
        if init is not None:
            self.initialize_parameters(method=init)

    def forward(self, inputs):
        x = self.convs(inputs)
        return x

    def initialize_parameters(self, method='xavier_uniform'):
        """
        Initialize the parameters of a PyTorch module using the specified method.

        Parameters:
        - module (torch.nn.Module): The PyTorch module whose parameters need to be initialized.
        - method (str): The initialization method. Default is 'xavier_uniform'.
                       Other options include 'xavier_normal', 'kaiming_uniform', 'kaiming_normal',
                       'orthogonal', 'uniform', 'normal', etc.

        Returns:
        None
        """
        for name, param in self.named_parameters():
            if 'weight' in name:
                if method == 'xavier_uniform':
                    init.xavier_uniform_(param)
                elif method == 'xavier_normal':
                    init.xavier_normal_(param)
                elif method == 'kaiming_uniform':
                    init.kaiming_uniform_(param, mode='fan_in', nonlinearity='relu')
                elif method == 'kaiming_normal':
                    init.kaiming_normal_(param, mode='fan_in', nonlinearity='relu')
                elif method == 'orthogonal':
                    init.orthogonal_(param)
                elif method == 'uniform':
                    init.uniform_(param, a=0.0, b=1.0)
                elif method == 'normal':
                    init.normal_(param, mean=0.0, std=1.0)
                else:
                    raise ValueError(f"Unsupported initialization method: {method}")

    @staticmethod
    def from_hparams(hparams):
        pools = hparams.pools if "pools" in hparams.keys() is not None else []
        batchnorm = hparams.batchnorm if "batchnorm" in hparams.keys() else False
        init = hparams.init if "init" in hparams.keys() else "xavier_uniform"
        return ConvNet(
            in_filters=hparams.in_filters,
            filters=hparams.filters,
            kernel_size=hparams.kernel_size,
            pools=pools,
            batchnorm=batchnorm,
            init=init,
            activation=hparams.activation,
            activate_output=hparams.activate_output,
        )

    def serialize(self):
        return dict(
            type=self.__class__,
            state_dict=self.state_dict(),
            params=dict(
                in_filters=self.in_filters,
                filters=self.filters,
                kernel_size=self.kernel_size,
                pools=self.pools,
                batchnorm=self.batchnorm,
                init=self.init,
                activation=self.activation,
                activate_output=self.activate_output,
            )
        )

    @staticmethod
    def deserialize(serialized):
        net = ConvNet(**serialized["params"])
        net.load_state_dict(serialized["state_dict"])
        return net


class DeconvNet(SerializableModule):
    """
    Parametric convolutional network
    based on Efficient-VDVAE paper

    :param in_filters: int, the number of input filters
    :param filters: list of int, the number of filters for each layer
    :param kernel_size: int or tuple of int, the size of the convolutional kernel
    :param pool_strides: int or tuple of int, the strides for the pooling layers
    :param unpool_strides: int or tuple of int, the strides for the unpooling layers
    :param activation: torch.nn.Module, the activation function to use
    """
    def __init__(self, in_filters, filters, kernel_size, unpools=None,
                 activation=nn.Softplus(), activate_output=False):
        super(DeconvNet, self).__init__()

        self.in_filters = in_filters
        self.filters = filters
        assert len(self.filters) > 0, "Must have at least one filter"

        if isinstance(kernel_size, int):
            kernel_size = [(kernel_size, kernel_size)] * (len(self.filters) - 1)
        elif isinstance(kernel_size, list):
            kernel_size = [(ks, ks) for ks in kernel_size]
        self.kernel_size = kernel_size

        if unpools is None:
            unpools = []
        self.unpools = unpools
        unpool_layers = [x[0] for x in self.unpools]
        unpool_strides = [x[1] for x in self.unpools]

        self.activation = activation
        self.activate_output = activate_output

        i = 0
        convs = nn.Sequential()
        if i in unpool_layers:
            convs.append(
                nn.ConvTranspose2d(in_channels=self.in_filters,
                                   out_channels=self.filters[0],
                                   kernel_size=self.kernel_size[0],
                                   stride=unpool_strides[0]),
                )
            #  convs.append(nn.BatchNorm2d(self.in_filters))
            if len(filters) != 1 or self.activate_output:
                convs.append(self.activation)
                convs.append(nn.Conv2d(in_channels=self.filters[0],
                                       out_channels=self.filters[0],
                                       kernel_size=self.kernel_size[i+1],
                                       padding="same"))

        for i in range(len(self.filters)-1):
            #  convs.append(nn.BatchNorm2d(self.filters[i]))
            convs.append(self.activation)

            if i + 1 in unpool_layers:
                convs.append(
                    nn.ConvTranspose2d(in_channels=self.filters[i],
                                       out_channels=self.filters[i],
                                       kernel_size=self.kernel_size[0],
                                       stride=unpool_strides[0]),
                )
                #  convs.append(nn.BatchNorm2d(self.filters[i]))
                convs.append(self.activation)
            convs.append(nn.Conv2d(in_channels=self.filters[i],
                                   out_channels=self.filters[i + 1],
                                   kernel_size=self.kernel_size[i+1],
                                   padding="same"))

        if self.activate_output:
            convs.append(self.activation)

        self.convs = nn.Sequential(*convs)

    def forward(self, inputs):
        x = self.convs(inputs)
        return x

    @staticmethod
    def from_hparams(hparams):
        return DeconvNet(
            in_filters=hparams.in_filters,
            filters=hparams.filters,
            kernel_size=hparams.kernel_size,
            unpools=hparams.unpools,
            activation=hparams.activation,
            activate_output=hparams.activate_output,
        )

    def serialize(self):
        return dict(
            type=self.__class__,
            state_dict=self.state_dict(),
            params=dict(
                in_filters=self.in_filters,
                filters=self.filters,
                kernel_size=self.kernel_size,
                unpools=self.unpools,
                activation=self.activation,
                activate_output=self.activate_output,
            )
        )

    @staticmethod
    def deserialize(serialized):
        p = serialized["params"]
        p["filters"] = p["filters"][1:]
        net = DeconvNet(**p)
        net.load_state_dict(serialized["state_dict"])
        return net


class BlockNet(SerializableModule):

    def __init__(self, **blocks):
        from ..block import InputBlock
        super(BlockNet, self).__init__()

        self.input_block, output = next(((block, output) for output, block in blocks.items()
                                         if isinstance(block, InputBlock)), None)
        self.input_block.set_output(output)
        self.output_block = next((block for _, block in blocks.items()
                                  if isinstance(block, self.OutputBlock)), None)

        self.blocks = nn.ModuleDict()
        for output, block in blocks.items():
            if not isinstance(block, (InputBlock, self.OutputBlock)):
                block.set_output(output)
                self.blocks.update({output: block})

    def forward(self, inputs):
        computed = self.input_block(inputs)
        computed = self.propogate_blocks(computed)
        output = self.output_block(computed)
        return output

    def propogate_blocks(self, computed):
        for block in self.blocks.values():
            output = block(computed=computed)
            if isinstance(output, tuple):
                computed, _ = output
            else:
                computed = output
        return computed

    def serialize(self):
        blocks = list()
        blocks.append(self.input_block.serialize())
        for block in self.blocks.values():
            blocks.append(block.serialize())
        blocks.append(self.output_block.serialize())
        return dict(
            type=self.__class__,
            blocks=blocks
        )

    @staticmethod
    def deserialize(serialized):
        blocks = OrderedDict()
        for block in serialized["blocks"]:
            blocks[block["output"]] = block["type"].deserialize(block)
        return BlockNet(**blocks)

    class OutputBlock(SerializableModule):
        """
        Final block of the model
        Functions like a SimpleBlock
        Only for use in BlockNet
        """
        def __init__(self, input_id):
            super(BlockNet.OutputBlock, self).__init__()
            self.input = input_id

        def forward(self, computed: dict) -> (tensor, dict, tuple):
            output = computed[self.input]
            return output

        def serialize(self):
            return dict(
                type=self.__class__,
                input=self.input,
                output="output"
            )

        @staticmethod
        def deserialize(serialized: dict):
            return BlockNet.OutputBlock(input_id=serialized["input"])




