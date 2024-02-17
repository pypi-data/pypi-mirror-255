import torch
from beartype import beartype
from typing import Callable


@beartype
def batchedProbAccept(s: "torch.Tensor", s_p: "torch.Tensor", probFn: Callable):
    """
    Batched probabilistic acceptance rule.

    Args:
        s (torch.Tensor) : Batched state tensor of shape (batch_size, num_dim)
        s_p (torch.Tensor) : Batched state tensor of shape (batch_size, num_dim)
        probFn (Callable) : function that takes in a tensor of configurations and returns the corresponding probability.
    """
    p_change = probFn(s, s_p)

    accept = torch.bernoulli(p_change)

    s = torch.where(torch.gt(accept.detach(), 0), s_p, s)

    return s
