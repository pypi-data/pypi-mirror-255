from torch import tensor
import torch

from .utils import OrderedModuleDict
from .elements.distributions import ConcatenatedDistribution
from .block import GenBlock
from .hvae import hVAE
from .utils import handle_shared_modules


class hSequenceVAE(hVAE):
    def __init__(self, blocks: OrderedModuleDict, init: dict = None):
        super(hSequenceVAE, self).__init__(blocks, init=init)

    def forward(self, inputs, stop_at=None, use_mean=False) -> (dict, dict):
        if isinstance(inputs, torch.Tensor):
            seq_len = inputs.shape[1]
            computed, distributions = dict(), dict()
            outputs, output_distributions = [], []
        elif isinstance(inputs, dict):
            seq_len = 1
            computed = inputs
            distributions = dict()
            outputs, output_distributions = [], []
        else:
            raise ValueError("Inputs must be Tensor or dict()")

        for i in range(seq_len):
            for j, block in enumerate(self.blocks.values()):
                if block.output in computed.keys():
                    continue
                if j == 0:
                    observation_computed, observation_distributions = \
                        block(inputs[:, i], use_mean=use_mean)
                    if i == 0:
                        batch_size = observation_computed[self.blocks[0].output].shape[0]
                        observation_computed = self._init_prior(observation_computed, batch_size)
                    computed.update(observation_computed)
                    distributions.update(observation_distributions)
                    continue

                computed, dist = block(computed, use_mean=use_mean)
                if dist is not None:
                    distributions[block.output] = dist
                if stop_at is not None and stop_at in computed.keys():
                    return computed, distributions

            outputs.append(computed[self.blocks[-1].output])
            output_distributions.append(distributions.pop(self.blocks[-1].output)[0])

            computed = {f'_{key}': value for key, value in computed.items()}
            distributions = {f'_{key}': value for key, value in distributions.items()}

        computed['output'] = torch.stack(outputs, dim=1)
        distributions['output'] = ConcatenatedDistribution(output_distributions, fuse='sum')
        return computed, distributions

    def sample_from_prior(self, seq_len: int, batch_size: int, temperatures: list) -> (tensor, dict):
        computed = self._init_prior(dict(), batch_size)
        distributions = dict()
        outputs, output_distributions = [], []
        with torch.no_grad():
            for i in range(seq_len):
                in_generator = False
                for j, block in enumerate(self.blocks.values()):
                    if isinstance(block, GenBlock):
                        in_generator = True
                    if in_generator:
                        computed, dist = block.sample_from_prior(computed, temperatures[i])
                        if dist:
                            distributions[block.output] = dist
                outputs.append(computed[self.blocks[-1].output])
                output_distributions.append(distributions.pop(self.blocks[-1].output)[0])
                computed = {f'_{key}': value for key, value in computed.items()}
                distributions = {f'_{key}': value for key, value in distributions.items()}

        computed['output'] = torch.stack(outputs, dim=1)
        distributions['output'] = ConcatenatedDistribution(output_distributions, fuse='sum')
        return computed, distributions

    def extrapolate(self, inputs: int, seq_len: int) -> (dict, dict):
        with torch.no_grad():
            computed, distributions = self(inputs)
            outputs, output_distributions = [], []
            for i in range(seq_len):
                in_generator = False
                for j, block in enumerate(self.blocks.values()):
                    if isinstance(block, GenBlock):
                        in_generator = True
                    if in_generator:
                        computed, dist = block.sample_from_prior(computed)
                        if dist:
                            distributions[block.output] = dist
                outputs.append(computed[self.blocks[-1].output])
                output_distributions.append(distributions.pop(self.blocks[-1].output)[0])
                computed = {f'_{key}': value for key, value in computed.items()}
                distributions = {f'_{key}': value for key, value in distributions.items()}

            output_name = "_"*seq_len + "output"
            computed['output'] = torch.cat([computed[output_name], torch.stack(outputs, dim=1)], dim=1)
            distributions['output'] = distributions[output_name].extend(output_distributions)
            return computed, distributions

    @staticmethod
    def deserialize(serialized):
        blocks = OrderedModuleDict()
        shared = dict()
        for block in serialized["blocks"]:
            deserialized = block["type"].deserialize(block)
            deserialized, shared = handle_shared_modules(deserialized, shared)
            blocks[block["output"]] = deserialized
        return hSequenceVAE(blocks, serialized["prior"])

    def visualize_graph(self) -> None:
        raise NotImplementedError()
