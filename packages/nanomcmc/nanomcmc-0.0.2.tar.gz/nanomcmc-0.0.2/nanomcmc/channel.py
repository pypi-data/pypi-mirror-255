import torch
from beartype import beartype


@beartype
def additiveNoise(s: "torch.Tensor", s_p: "torch.Tensor"):
    """
        Updates s to s_p by adding constant 'noise' equal to s - s_p.

    Args:
        s (torch.Tensor) : Batched state tensor
        s_p (torch.Tensor) : Batched state tensor
    """

    return s + (s_p - s).detach()
