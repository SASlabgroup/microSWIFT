## GPSwaves.py Test Script - random values onboard microSWIFT
# Written By: EJ Rainville, Spring 2021
import numpy as np

# Define random vectors to be tested
amplitude = 3
u = amplitude * np.random.rand(1, 512)
v = amplitude * np.random.rand(1, 512)
z = amplitude * np.random.rand(1, 512)
fs = 4

# Run GPSwaves.py as a function 
from GPSwaves import GPSwaves
Hs, Tp, Dp, E, f, a1, b1, a2, b2 = GPSwaves(u, v, z, fs)

# Print shapes of all outputs
print('Hs = ', Hs)
print('Tp = ', Tp)
print('Dp = ', Dp)
print('E = ', E.shape)
print('f shape = ', f.shape)
print('a1 shape = ', a1.shape )
print('b1 shape = ', b1.shape)
print('a2 shape = ', a2.shape)
print('b2 shape = ', b2.shape)