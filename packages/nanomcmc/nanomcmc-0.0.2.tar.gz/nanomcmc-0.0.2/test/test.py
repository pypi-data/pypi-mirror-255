"""
File: test.py
Author: Blake Wilson 
Email: wilso692@purdue.edu

Description:
    Test file for nanoml-template.
"""

import nanomcmc as mcmc
import polytensor
import torch


def test_docs():
    """
    Test that the docs examples work.
    """

    import nanomcmc as mcmc

    # Random Walk
    acceptanceRule = lambda x, x_p: x_p  # Automatically accept all proposals
    proposer = lambda x: torch.bernoulli(torch.ones_like(x) * 0.5)  # Random walk

    steps = 10

    mcmc_layer = mcmc.MCMC(
        proposer=proposer, acceptanceRule=acceptanceRule, steps=steps
    )

    x = torch.tensor([[1, 0, 1], [1, 1, 1]], dtype=torch.float32)

    mcmc_layer(x)


def test_tmatrix(t_matrix, x, out):
    x = torch.tensor([[1], [1]])

    tprop = mcmc.proposer.TransitionMatrix(
        tMatrix=torch.tensor([[0, 1], [1, 0]], dtype=torch.float32),
    )

    tmatrix = mcmc.MCMC(proposer=tprop, acceptanceRule=lambda x, x_hat: x_hat, steps=1)


def testPackage():
    """
    Main function for test.py
    """

    print("Testing nanomcmc package...")

    orig_coefficients = polytensor.generators.coeffPUBORandomSampler(
        n=10, num_terms=[10, 5, 3], sample_fn=lambda: torch.rand(1)
    )

    poly = polytensor.SparsePolynomial(coefficients=orig_coefficients)

    x = torch.bernoulli(torch.ones(2, 10) * 0.5)

    uniformBoltzmann = mcmc.Boltzmann(
        proposer=lambda s: torch.bernoulli(torch.ones_like(s) * 0.5),
        energy_fn=lambda x: poly(x),
        steps=1,
    )

    # print(uniformBoltzmann(x))

    x = torch.tensor([[1], [1]])

    tprop = mcmc.proposer.TransitionMatrix(
        tMatrix=torch.tensor([[0, 1], [1, 0]], dtype=torch.float32),
    )

    tmatrix = mcmc.MCMC(proposer=tprop, acceptanceRule=lambda x, x_hat: x_hat, steps=1)

    print("Test complete.")
