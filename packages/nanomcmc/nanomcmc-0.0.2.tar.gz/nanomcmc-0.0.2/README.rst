.. nanomcmc documentation master file, created by
   sphinx-quickstart on Sat Jan 20 11:25:10 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: /docs/source/_static/logo.png
  :align: center
  :width: 100
  :alt: nanomcmc logo 



``nanomcmc``
==============

``nanomcmc`` is a python package for extremely parallelized, autograd-friendly MCMC with Pytorch. MCMC is a very versatile algorithm. It can be used to realize Boltzmann distributions, random walks, scramblers, dynamics, and many other applications. 

Why ``nanomcmc``?

  My research group is working on several energy model projects, so I needed a way to quickly prototype MCMC algorithms. I also wanted to be able to run them on a GPU and take advantage of PyTorch on the backend. I couldn't find any existing packages that were simple and demonstrated significant speed-up; so I wrote my own. I hope you find it useful too!

.. figure:: ./docs/source/_static/cuda_vs_cpu_sparse.svg
  :align: center
  :width: 80%

  Computation time and speed-up for computing 100 steps of MCMC on a 100 bit system with a Metropolis-Hastings acceptance rule and a sparse 3-degree, 300 monomial polynomial energy function (polytensor).  Left y-axis) Time to compute MCMC on a CPU and GPU. Right y-axis) Speedup of GPU over CPU. x-axis) the number of parallel chains, or batch size, from 1 chain to 1 million chains. The black line is the time for a CPU (Intel Xeon W-2245 @ 3.9Ghz) and the green line is the time for an A5000 GPU. The purple dashed line shows the speed-up of the GPU over the CPU for each parallel chain size.


Documentation
-------------
The documentation is hosted on `Github Pages <https://nanometaml.github.io/mcmc/docs/build/html/>`_.

Quick Start
-----------

To use the latest stable version of ``nanomcmc``, install it using ``pip`` from the command line:

.. code-block:: console

   $ pip install nanomcmc


For the latest development version, install it directly from this repo:

.. code-block:: console

   $ python -m venv .venv
   $ source .venv/bin/activate
   $ (.venv) python -m pip install git+https://github.com/btrainwilson/nanomcmc.git

Or, if you want to develop ``nanomcmc``, install it in editable mode:

.. code-block:: console

    $ git clone git+https://github.com/nanometaml/mcmc.git
    $ python -m pip install -e nanomcmc

Examples
--------
All of the following examples assume that you have imported ``nanomcmc``:

.. code-block:: python

    import nanomcmc as mcmc

Scrambler
~~~~~~~~~

Let's start with a simple example. We have a system with 3 binary variables. We want to jump around randomly to scramble the bits. 

.. code-block:: python

    # Initial state
    s_0 = torch.tensor([[1, 0, 1], [1, 1, 1]], dtype=torch.float32)

Uniform Scrambler 
^^^^^^^^^^^^^^^^^^^^^^

We can define a scrambler as follows. We want to randomly flip each bit with a probability of 0.5.



$$\\mathbf{s}'_{t+1} \\sim p(\\mathbf{s}'_{t+1} \\vert \\mathbf{s}_{t}) = 2^-n $$

Which is equivalent to choosing each bit with a fair coin,


$$\\mathbf{s}'_{t+1, i} \\sim \\text{Bernoulli}(0.5)$$


.. code-block:: python

    # Random uniform proposer
    proposer = lambda s: torch.bernoulli(torch.ones_like(s) * 0.5)  

Acceptance Rule
^^^^^^^^^^^^^^^
To keep things simple, we'll always accept the new state.

Our acceptance rule is to always accept the new state,


$$a(\\mathbf{s}_{t+1} \\vert \\mathbf{s}'_{t+1}, \\mathbf{s}_{t}) = \\delta(\\mathbf{s}_{t+1} - \\mathbf{s}'_{t+1})$$

$$\\mathbf{s}_{t+1} = \\mathbf{s}'_{t+1}$$

.. code-block:: python

    # Automatically accept all proposals
    acceptanceRule = lambda s, s_p: s_p  

MCMC
^^^^

We put it all together using the ``MCMC`` class:

.. code-block:: python

    scrambler = mcmc.MCMC(
        proposer=proposer, acceptanceRule=acceptanceRule, steps=1
    )

    scrambler(s_0)

    >>> tensor([[0., 1., 1.],
                [1., 1., 1.]])



Random Walk
~~~~~~~~~~~

Let's try a more interesting example. We have our same system with 3 binary variables and we want to perform a random walk.

.. code-block:: python

    # Automatically accept all proposals
    acceptanceRule = lambda s, s_p: s_p  

    def proposer(s):
        # Chooses a random bit flip
        s_f = torch.distributions.OneHotCategorical(probs=torch.ones_like(s) / s.shape[-1]).sample()
        # Flips the bit
        return torch.remainder(s + s_f, 2)

    # 1 step in the chain
    steps = 1

    # Initial state
    s_0 = torch.tensor([[1, 0, 1], [1, 1, 1]], dtype=torch.float32)

    scrambler = mcmc.MCMC(
        proposer=proposer, acceptanceRule=acceptanceRule, steps=steps
    )

    scrambler(s_0)

    >>> tensor([[1., 1., 1.],
                [0., 1., 1.]])

Notices how the output is only one step away from the input. Increase the number of steps to get a longer random walk and increase the Hamming distance.

Boltzmann Sampling
~~~~~~~~~~~~~~~~~~

We'll start by building a simple Boltzmann sampler. The Boltzmann distribution is given by:


$$z \\sim \\mu(z) = e^{-E(z) / \\tau} / Z$$

where $z \\in \\{0, 1\\}^n$ is a bit string, $E(z)$ is the energy of $z$, and $\\tau$ is a temperature $\\tau \\in \\mathbb{R}_{\\geq 0}$. We start by defining our energy function as a polynomial using `polytensor <https://btrainwilson.github.io/polytensor>`_,

.. code-block:: python

   import polytensor

   orig_coefficients = polytensor.generators.coeffPUBORandomSampler(
        n=n, num_terms=[n, n, n, n], sample_fn=lambda: torch.rand(1, device=device)
    )

   poly = polytensor.SparsePolynomial(coefficients=orig_coefficients, device=device)

Here, poly evaluates $E(z)$. Then, we define our Boltzmann distribution using the ``Boltzmann`` class,

.. code-block:: python

    tau = 1.0

    uniformBoltzmann = mcmc.Boltzmann(
        proposer=lambda s: torch.bernoulli(torch.ones_like(s) * 0.5),
        energy_fn=lambda x: poly(x) / tau,
        steps=s,
    )

The ``Boltzmann`` class takes a proposer, an energy function, and the number of steps to take in the chain. The proposer is the same as before, a uniform Bernoulli proposer. The energy function is the polynomial we defined above divided by the temperature. The temperature is a hyperparameter that controls the variance of the Boltzmann distribution. The higher the temperature, the more uniform the distribution. The lower the temperature, the more peaked the distribution. The temperature is a hyperparameter that can be tuned to your application.

Now, we can sample from the Boltzmann distribution,

.. code-block:: python

    uniformBoltzmann(x)

To recreate the plot at the top of the page, run the following code,

.. code-block:: python

    import time
    import logging
    import numpy as np
    import torch
    import nanomcmc as mcmc
    import polytensor
    import matplotlib.pyplot as plt


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
            n = 100       # number of variables in polynomial
            s = 100       # number of steps
            d = 3

            print("Testing CUDA")
            cuda_time.append(batchedTest(b, n, s, d, device="cuda"))

            print("Testing CPU")
            cpu_time.append(batchedTest(b, n, s, d, device="cpu"))

        return cuda_time, cpu_time


    if __name__ == "__main__":

        cuda_time, cpu_time = benchmarkPackage()

        print(cuda_time)
        print(cpu_time)


        print("Plotting results")

        b = [10 ** i for i in range(len(cpu_time))]

        # Create a figure and a single subplot
        fig, ax1 = plt.subplots()

        # First plot: Log-log plot for cuda_time and cpu_time on the left y-axis
        ax1.loglog(b, cuda_time, label="cuda - A5000", c="green")
        ax1.loglog(b, cpu_time, label="cpu - Intel Xeon W-2245", c="black")
        ax1.set_xlabel("Batch Size (# Vectors)")
        ax1.set_ylabel("Computation Time (s)", color="black")
        ax1.tick_params(axis="y", labelcolor="black")
        ax1.set_title("Sparse Polynomial MCMC Performance and GPU Speed-up")
        ax1.legend(loc="upper left")

        # Create a second y-axis for the speed-up plot
        ax2 = ax1.twinx()
        ax2.plot(b, cpu_time / cuda_time, c="purple", label="GPU Speed-up", linestyle="dashed")
        ax2.set_ylabel("Speed-up", color="purple")
        ax2.tick_params(axis="y", labelcolor="purple")
        ax2.legend(loc="upper right")

        # Adjust layout and save the figure
        fig.tight_layout()
        plt.savefig("./cuda_vs_cpu_with_speedup.svg")



Future Tutorials
----------------

1. Quantum Annealing



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Contributing
------------

We welcome contributions! 

To set up the test environment (.tenv virtual environment), run the following commands:

.. code-block:: console

    $ git clone git+https://github.com/btrainwilson/mcmc.git
    $ cd mcmc
    $ make .tenv
    $ source .tenv/bin/activate

This will handle installing the development dependencies and setting up the virtual environment. 

Testing
~~~~~~~~~~~~~

To run the tests, run the following command:

.. code-block:: console

    $ make test

If everything is set up properly, the tests should pass with green text at the bottom. 

Documentation
~~~~~~~~~~~~~

To build the documentation, run the following command:

.. code-block:: console

    $ make doc

This will build the documentation in the ``docs/build`` directory. 
To view the documentation,  

.. code-block:: console

    $ make serve 

and navigate to `localhost:8018` in your browser.

Pull Requests
~~~~~~~~~~~~~

To submit a contribution, fork the repo and submit a pull request with your changes. We will review the request by running our test suites to ensure the interface is not broken and then check for code cleanliness and correctness. To increase the chances of accepting a PR, build a unit test in the test/ directory as a part of the PR.  




