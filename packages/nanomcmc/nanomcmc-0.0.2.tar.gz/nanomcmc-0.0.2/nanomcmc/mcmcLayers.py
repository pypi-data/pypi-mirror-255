from .mcmc import MCMCLayer
from . import acceptRule, energyFns
from typing import Callable, Union
from beartype import beartype


class Boltzmann(MCMCLayer):
    """
    A Boltzmann MCMCLayer using the Metropolis-Hastings acceptance rule with an energy function to realize a Boltzmann distribution.

    Args:
        Callable: proposer - A function that takes a sample and returns a new sample.
        Callable: energy_fn -  A function that takes a sample and returns a scalar energy.
        float: temperature - The temperature of the Boltzmann distribution.
    """

    @beartype
    def __init__(
        self,
        proposer: Callable,
        energy_fn: Callable,
        temperature: Union[float, int] = 1.0,
        steps: int = 10,
    ):
        if temperature < 0:
            raise ValueError("Temperature must be positive.")

        self.temperature = temperature
        self.energy_fn = energy_fn

        probFn = lambda s, s_p: energyFns.clampedBoltzmannFactor(
            s,
            s_p,
            energy_fn=lambda x: energy_fn(x) / self.temperature,
        )

        acceptanceRule = lambda s, s_p: acceptRule.batchedProbAccept(
            s, s_p, probFn=probFn
        )

        super().__init__(proposer=proposer, acceptanceRule=acceptanceRule, steps=steps)


class Identity(MCMCLayer):
    """
    Mock MCMCLayer that returns the input.
    """

    def __init__(self):
        super().__init__(
            proposer=lambda x: x,
            acceptanceRule=lambda x, x_hat: x,
            steps=1,
        )
