## GPSwaves.py Test Script 
# Written By: EJ Rainville, Spring 2021

# Import Packages
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from termcolor import colored

# Imports from script
import sys
import numpy as np
from struct import *
from logging import *
from datetime import datetime
import time
import struct
from time import sleep
from GPSwaves import GPSwaves

print('Packages Loaded')

# Define random u and v
num_points = 240000
ran = 3
u = ran * np.random.random_sample(num_points) 
v = ran * np.random.random_sample(num_points) 
z = ran * np.random.random_sample(num_points) 
fs = 5

# Run the GPSwaves.py function
from process_data import main
print('process data imported')
# Hs, Tp, Dp, E, f, a1, b1, a2, b2 = GPSwaves(u, v, z, fs)
# print('Hs = ', Hs)
# print('Tp = ', Tp)
# print('Dp = ', Dp)
# print('E = ', E)