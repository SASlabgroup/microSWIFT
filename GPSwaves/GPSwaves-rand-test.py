## GPSwaves.py Test Script 
# Written By: EJ Rainville, Spring 2021

# Import Packages
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from termcolor import colored
print('Packages Loaded')

# # Define random u and v
# num_points = 240000
# ran = 3
# u = ran * np.random.random_sample(num_points) 
# v = ran * np.random.random_sample(num_points) 
# z = ran * np.random.random_sample(num_points) 
# fs = 5

# Read in Raw SWIFT Data

# Run the GPSwaves.py function
from GPSwaves import GPSwaves
Hs, Tp, Dp, E, f, a1, b1, a2, b2 = GPSwaves(u, v, z, fs)
print('Hs = ', Hs)
print('Tp = ', Tp)
print('Dp = ', Dp)
print('E = ', E)