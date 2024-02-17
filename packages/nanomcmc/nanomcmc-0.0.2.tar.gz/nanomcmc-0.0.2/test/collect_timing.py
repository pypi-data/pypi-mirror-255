"""
File: collect_timing.py
Author: Blake Wilson 
Email: wilso692@purdue.edu

Description:
    Tests nanomcmc package with various platforms.
"""

import nanomcmc as mcmc
import logging
import time
import polytensor
import torch
import numpy as np


def batchedTest(b, n, s, d, device):

    num_terms = [n] * d

    orig_coefficients = polytensor.generators.coeffPUBORandomSampler(
        n=n, num_terms=num_terms, sample_fn=lambda: torch.rand(1, device=device)
    )

    poly = polytensor.SparsePolynomial(coefficients=orig_coefficients, device=device)

    x = torch.bernoulli(torch.ones(b, n, device=device) * 0.5)

    uniformBoltzmann = mcmc.Boltzmann(
        proposer=lambda s: torch.bernoulli(torch.ones_like(s) * 0.5),
        energy_fn=lambda x: poly(x),
        steps=s,
    )

    start = time.time()
    uniformBoltzmann(x)
    end = time.time()

    return end - start


def benchmarkPackage():
    """
    Main function for test.py

    """
    logging.info("Benchmarking nanomcmc package")
    cuda_time = []
    cpu_time = []

    for b_i in range(7):
        b = 10 ** b_i
        # b = 1000000  # batch size
        n = 100  # number of variables in polynomial
        s = 100  # number of steps
        d = 3

        print("Testing CUDA")
        cuda_time.append(batchedTest(b, n, s, d, device="cuda"))

        print("Testing CPU")
        cpu_time.append(batchedTest(b, n, s, d, device="cpu"))

    return cuda_time, cpu_time


if __name__ == "__main__":

    cuda_time, cpu_time = benchmarkPackage()

    np.save("./test/data/cuda_time.npy", cuda_time)
    np.save("./test/data/cpu_time.npy", cpu_time)

    print(cuda_time)
    print(cpu_time)
