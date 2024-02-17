import torch
from torch import tensor, distributions as dist

from .. import params


dist.distribution.Distribution.set_default_validate_args(False)


def generate_distribution(mu: tensor, sigma: tensor = None, distribution: str = 'normal',
                          sigma_nonlin: str = None, sigma_param: str = None) -> dist.Distribution:
    """
    Generate parameterized distribution

    :param mu: the mean of the distribution
    :param sigma: the standard deviation of the distribution, not needed for mixture of logistics
    :param distribution: 'mixtures_of_logistics', 'normal', 'laplace
    :param sigma_nonlin: 'logstd', 'std'
    :param sigma_param: 'var', 'std'
    :return: torch.distributions.Distribution object
    """
    from .. import params
    model_params = params.model_params

    sigma_nonlin = model_params.distribution_base if sigma_nonlin is None else sigma_nonlin
    sigma_param = model_params.distribution_sigma_param if sigma_param is None else sigma_param
    beta = model_params.gradient_smoothing_beta

    if sigma_nonlin == 'logstd':
        sigma = torch.exp(sigma * beta)
    elif sigma_nonlin == 'std':
        sigma = torch.nn.Softplus(beta=beta)(sigma)
    elif sigma_nonlin != 'none':
        raise ValueError(f'Unknown sigma_nonlin {sigma_nonlin}')

    if sigma_param == 'var':
        sigma = torch.sqrt(sigma)
    elif sigma_param != 'std':
        raise ValueError(f'Unknown sigma_param {sigma_param}')

    if distribution == 'normal':
        return dist.Normal(loc=mu, scale=sigma)
    elif distribution == 'laplace':
        return dist.Laplace(loc=mu, scale=sigma)
    else:
        raise ValueError(f'Unknown distr {distribution}')


class MixtureOfGaussians(dist.mixture_same_family.MixtureSameFamily):
    def __init__(self, logits, loc, scale, validate_args=None):
        component = dist.Normal(loc=loc, scale=scale)
        super(MixtureOfGaussians, self).__init__(
            mixture_distribution=dist.Categorical(logits=logits),
            component_distribution=dist.Independent(component, 1),
            validate_args=validate_args,
        )

class MixturesOfLogistics(dist.mixture_same_family.MixtureSameFamily):
    def __init__(self, logits, loc, scale, validate_args=None):
        component = self._logistic(loc, scale)
        super(MixturesOfLogistics, self).__init__(
            mixture_distribution=dist.Categorical(logits=logits),
            component_distribution=dist.Independent(component, 1),
            validate_args=validate_args,
        )

    @staticmethod
    def _logistic(loc, scale):
        return dist.TransformedDistribution(
            dist.Uniform(torch.zeros(loc.shape), torch.ones(loc.shape)),
            [dist.SigmoidTransform().inv, dist.AffineTransform(loc, scale)]
        )


class ConcatenatedDistribution(dist.distribution.Distribution):
    """
    Concatenated distribution

    """
    def __init__(self, distributions: list, fuse: str = 'sum'):
        self.distributions = distributions
        self.fuse = fuse
        dbs = distributions[0].batch_shape
        batch_shape = torch.Size([dbs[0], len(distributions), *dbs[1:]])
        super(ConcatenatedDistribution, self).__init__(batch_shape=batch_shape)

    def extend(self, distributions: list):
        self.distributions.extend(distributions)
        return ConcatenatedDistribution(self.distributions, self.fuse)

    @property
    def mean(self) -> torch.Tensor:
        means = [d.mean for d in self.distributions]
        means = torch.stack(means, dim=1)
        return means

    @property
    def variance(self) -> torch.Tensor:
        variances = [d.variance for d in self.distributions]
        variances = torch.stack(variances, dim=0)
        return variances

    def rsample(self, sample_shape: torch.Size = torch.Size()) -> torch.Tensor:
        samples = [d.rsample(sample_shape) for d in self.distributions]
        samples = torch.stack(samples, dim=0)
        return samples

    def log_prob(self, value: torch.Tensor) -> torch.Tensor:
        log_probs = [d.log_prob(value[:, i]) for i, d in enumerate(self.distributions)]
        log_probs = torch.stack(log_probs, dim=1)
        if self.fuse == 'sum':
            log_probs = torch.sum(log_probs, dim=1)
        elif self.fuse == 'mean':
            log_probs = torch.mean(log_probs, dim=1)
        else:
            raise ValueError(f'Unknown fuse {self.fuse}')
        return log_probs

    def entropy(self) -> torch.Tensor:
        entropies = [d.entropy() for d in self.distributions]
        entropies = torch.stack(entropies, dim=0)
        if self.fuse == 'sum':
            entropies = torch.sum(entropies, dim=0)
        elif self.fuse == 'mean':
            entropies = torch.mean(entropies, dim=0)
        else:
            raise ValueError(f'Unknown fuse {self.fuse}')
        return entropies


