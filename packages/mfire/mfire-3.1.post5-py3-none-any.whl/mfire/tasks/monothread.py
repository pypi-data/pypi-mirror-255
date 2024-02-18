# to prevent numpy to use multithreading
import os

print("mono threading for numpy")
os.environ["OPENBLAS_NUM_THREADS"] = "1"  # on pc
os.environ["MKL_NUM_THREADS"] = "1"  # on hpc
