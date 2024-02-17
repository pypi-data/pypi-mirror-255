import torch
import math
from typing import Callable
from .utils import stringToUint, uintToString


class TransitionMatrix:
    """
    Uses transition matrix to sample next state.

    Args:
        tMatrix (torch.Tensor): A tensor representing the transition matrix.
        toMatElem (Callable): A function that converts a bitstring to an element of the transition matrix.
        fromMatElem (Callable): A function that converts an element of the transition matrix to a bitstring.

    """

    def __init__(
        self,
        tMatrix: "torch.Tensor",
        toMatElem: Callable = None,
        fromMatElem: Callable = None,
    ):
        self.tMatrix = tMatrix

        if self.tMatrix.shape[0] != self.tMatrix.shape[1]:
            raise ValueError("Transition matrix must be square")

        if toMatElem is None:
            self.toMatElem = lambda x: stringToUint(x)
        else:
            self.toMatElem = toMatElem

        if fromMatElem is None:
            self.fromMatElem = lambda x: uintToString(
                x, int(math.log2(self.tMatrix.shape[0]))
            )

    def __call__(self, s: "torch.Tensor") -> "torch.Tensor":
        # Converts to element index for transition matrix
        s = self.toMatElem(s)

        # Samples state row
        s_sample = self.tMatrix[s]
        s_next = torch.distributions.OneHotCategorical(probs=s_sample).sample()
        s_label = torch.argmax(s_next, dim=-1)
        return self.fromMatElem(s_label)
