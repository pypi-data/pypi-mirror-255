import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

plt.figure()
cuda_time = np.load("./test/data/cuda_time.npy")
cpu_time = np.load("./test/data/cpu_time.npy")
b = [10 ** i for i in range(len(cpu_time))]

plt.loglog(b, cuda_time, label="cuda - A5000", c="green")
plt.loglog(b, cpu_time, label="cpu - Intel Xeon W-2245 ", c="black")
plt.xlabel("Batch Size (# Vectors)")
plt.ylabel("Computation Time (s)")
plt.title("Sparse Polynomial MCMC ")
plt.legend()
plt.savefig("./test/data/cuda_vs_cpu_sparse.svg")
