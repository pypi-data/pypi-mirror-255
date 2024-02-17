import torch
from beartype import beartype
from typing import Callable, Union, Dict


class MCMCLayer(torch.nn.Module):
    """
    NN layer that runs a MCMC chain for a specified number of steps

    Args:

        Callable: proposer
            Input: torch.tensor
            Output: torch.tensor

        Callable: acceptanceRule
            A function whose input is two tensors and output a single tensor

        int: steps
            Number of MCMC steps

    Returns
        x: tensor
            The final state of the MCMC chain
    """

    def __init__(self, proposer: Callable, acceptanceRule: Callable, steps: int):
        super(MCMCLayer, self).__init__()

        self.proposer = proposer
        self.acceptanceRule = acceptanceRule

        if steps < 1:
            raise ValueError("Number of steps must be positive.")

        self.steps = steps

    @beartype
    def forward(
        self, s: "torch.Tensor", steps: Union[int, None] = None
    ) -> "torch.Tensor":
        """
        Runs the MCMC chain for the specified number of steps and returns
        the final state.

        Args:
            s (torch.Tensor): Initial state of the chain
            steps (int): Number of steps to run

        Returns:
            torch.Tensor: Final state of the MCMC chain

        """

        steps = steps if steps is not None else self.steps

        if steps < 1:
            raise ValueError("Number of steps must be positive.")

        for _ in range(steps):
            x_hat = self.proposer(s)
            s = self.acceptanceRule(s, x_hat)

        return s

    @beartype
    def validate(
        self, s: "torch.Tensor", steps=None, log=False
    ) -> Dict[str, "torch.Tensor"]:
        """
        Runs the MCMC chain for the specified number of steps and returns
        a batched list of tensors of all states and proposed states.

        Args:
            s (torch.Tensor): Initial state of the chain
            steps (int): Number of steps to run

        Returns:
            Dict[str, torch.Tensor]: Final state of the MCMC chain
        """

        steps = steps if steps is not None else self.steps

        if steps < 1:
            raise ValueError("Number of steps must be positive.")

        s_list = [s]
        s_p_list = []

        for _ in range(steps):
            s_p = self.proposer(s)
            s_p_list.append(s_p)
            s = self.acceptanceRule(s, s_p)
            s_list.append(s)

        return {"chosen": s_list, "proposed": s_p_list}
