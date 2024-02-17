import torch
import itertools
import functools
from typing import Callable, Union
from beartype import beartype


@beartype
def boltzmannFactor(
    s: "torch.Tensor",
    s_p: "torch.Tensor",
    energy_fn: Callable,
) -> "torch.Tensor":
    """
    Computes the Boltzmann factor for the specified system.
    """
    return torch.exp(-1 * (energy_fn(s_p) - energy_fn(s)))


@beartype
def clampedBoltzmannFactor(
    s: "torch.Tensor",
    s_p: "torch.Tensor",
    energy_fn: Callable,
) -> "torch.Tensor":
    """
        Computes the Boltzmann factor.

    Args:
        s (torch.Tensor) : Batched state tensor of shape (batch_size, num_dim)
        s_p (torch.Tensor) : Batched state tensor of shape (batch_size, num_dim)
        energy_fn (function) : function that takes in a tensor of configurations and returns the corresponding energy.
    """

    # Is the proposed state lower energy than the current state?
    e_diff = energy_fn(s) - energy_fn(s_p)

    # If the proposed state is lower energy, automatically accept it. Otherwise, accept with probability prop to exp(-|energy(x_hat) - energy(x_hat)|).
    # By clamping all states such that e_diff < 0 to 0, we guarantee that they will be accepted.
    # Because e^(0) is 1, the probability of acceptance is 1. Else, the probability is prop to e^(-e_diff / temperature).

    e_clamped = torch.nn.functional.relu(-1 * e_diff)

    return torch.exp(-1 * e_clamped)


def absBoltzmanFactor(
    s: "torch.Tensor",
    s_p: "torch.Tensor",
    energy_fn: Callable,
) -> "torch.Tensor":
    """
    Computes the boltzmann factor for the specified system using the absolute value of the different in energy.
    Args:
        s (torch.Tensor) : Batched state tensor of shape (batch_size, num_dim)
        s_p (torch.Tensor) : Batched state tensor of shape (batch_size, num_dim)
        energy_fn (function) : function that takes in a tensor of configurations and returns the corresponding energy.

    """

    return torch.exp(-1 * torch.abs(energy_fn(s_p) - energy_fn(s)))


def boltzmann_factor(
    x: "torch.Tensor",
    H: "torch.Tensor",
    energy_fn: Callable,
    temperature: Union[float, int] = 1,
):
    """
    Computes the boltzmann factor for the specified system.

    Args:
        x (torch.Tensor) : Batched configuration tensor of shape (batch_size, num_dim)
        H (torch.Tensor) : Batched energy matrices of shape (batch_size, num_dim, num_dim)
        temperature (float) : Scalar representing the temperature of the system.

    Returns:
        torch.Tensor : The boltzmann factor for each configuration in the batch.
    """
    energies = energy_fn(x, H)
    return torch.exp(-energies / temperature)


def boltzmann_partition_fn(num_spins, interactions, temperature=1):
    """
    Computes the exact Boltzmann partition function for the specified system.

    Args:
        num_spins (int) : int representing the number of spins in the system.
        interactions (torch.Tensor) : Tensor of shape (num_spins, num_spins) representing the interaction graph between spins.
        temperature (float) : Scalar representing the temperature of the system.

    Returns:
        float: Partition function.
        torch.Tensor : Energy vector of size (2**num_spins) that holds the energy of all configurations of the system.
    """
    energy_fn = functools.partial(
        boltzmann_factor, H=interactions, temperature=temperature
    )
    return partition_fn(energy_fn, num_spins)


def partition_fn(energy_fn, num_spins, basis=[0, 1]):
    """
    Computes the partition function for the specified system given an energy function.

    Complexity: O(d^n) where d is the number of basis states and n is the number of spins.

    Args:
        energy_fn (function) : function that takes in a tensor of configurations and returns the corresponding energy.
        num_spins (int) : int representing the number of spins in the system.
        basis (list): list of possible states for each spin

    Returns:
        float : Partition function.
        torch.Tensor : Energy vector of size (2**num_spins) that holds the energy of all configurations of the system.
    """
    # Generate all configurations
    configurations = torch.FloatTensor(list(itertools.product(basis, repeat=num_spins)))

    # Query energy function on all configurations
    energies = energy_fn(configurations)

    # Compute partition function
    partition = energies.sum()

    return partition, energies


def rydberg_energy(x, positions, detuning, c6=1, degree=6):
    """
    Computes the energy of a Rydberg system given the Rydberg excitations, x, and their positions.

    Args:
        positions (torch.Tensor) : Tensor of shape (batch_size, num_atoms, 3) representing the positions of the atoms.
        x (torch.Tensor) : Tensor of shape (batch_size, num_atoms) representing if a site is in the Rydberg state.
        c6 (float) : Scalar representing the coefficient of the sixth power term in the interaction strength.

    Returns:
        torch.Tensor: Energies of all configurations in x.
    """
    # I tried to use correct units but saw that the energy was off by a huge factor. Need to fix later.
    hbar_Mega_micro = 1e-5  # 1.054571817e-34 * 1e6 * 1e6

    differences = positions.unsqueeze(-2) - positions.unsqueeze(
        -3
    )  # computes rydberg energy of solution
    distances = torch.norm(differences, dim=-1)

    diagonals = torch.eye(int(distances.size(dim=-1)), device=distances.device).view(
        distances.shape
    )  # creates identity mat based on distances's last two dims

    distances = distances + diagonals

    c6 = c6 ** (degree / 6)

    delta = torch.sum(detuning.unsqueeze(0) * x, dim=1)  # broadcasting

    x = x.unsqueeze(-1)

    tensor_prod = x * torch.transpose(x, 1, 2)

    # Remove diagonal values
    tensor_prod = tensor_prod * (
        1 - torch.eye(tensor_prod.shape[1], device=x.device).unsqueeze(0)
    )

    energy = c6 * tensor_prod / torch.pow(distances, degree)

    # Remove nan values
    energy = torch.nan_to_num(energy)

    energy = torch.sum(energy, dim=(1, 2))

    energy = delta + energy

    return energy * hbar_Mega_micro


def spectralGap(boltzmann_factor_fn, num_spins):
    partition, energies = partition_fn(
        energy_fn=boltzmann_factor_fn, num_spins=num_spins
    )
    return torch.sort(energies)[0][1] - torch.sort(energies)[0][0]
