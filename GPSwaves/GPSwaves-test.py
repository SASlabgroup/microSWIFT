## GPSwaves.py Test Script 
# Written By: EJ Rainville, Spring 2021

# Import Packages
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from termcolor import colored
print('Packages Loaded')

# Import Test Data and Test Output
test_data = sio.loadmat('GPSwaves-testdata-out.mat')

# Organize Data into Individual Componenets
# Test Data
u = list(np.squeeze(test_data['u']))
v = list(np.squeeze(test_data['v']))
z = list(np.squeeze(test_data['z']))
fs = float(np.squeeze(test_data['fs']))
print('Test Data Loaded')

# Test Data Output
Hs_t = float(np.squeeze(test_data['Hs']))
Tp_t = float(np.squeeze(test_data['Tp']))
Dp_t = float(np.squeeze(test_data['Dp']))
E_t= list(np.squeeze(test_data['E']))
f_t = list(np.squeeze(test_data['f']))
a1_t = list(np.squeeze(test_data['a1']))
b1_t = list(np.squeeze(test_data['b1']))
a2_t = list(np.squeeze(test_data['a2']))
b2_t = list(np.squeeze(test_data['b2']))
print('Test Output Loaded')

# Run GPSwaves.py as a function 
from GPSwaves import GPSwaves
Hs, Tp, Dp, E, f, a1, b1, a2, b2 = GPSwaves(u, v, z, fs)
# print(Hs, Tp, Dp, E, f, a1, b1, a2, b2)

# Test Output for the GPSwaves.py function
precision = 0.0001
# Test Hs
if(np.abs(Hs-Hs_t) <= precision ):
    print(colored('======== Test Hs Passed ========', 'green'))
else:
    print(colored('Hs Test Failed, Hs = ' + str(Hs) + ', Hs_t = ' + str(Hs_t), 'red'))

# Test Tp
if(np.abs(Tp-Tp_t) <= precision ):
    print(colored('======== Test Tp Passed ========', 'green'))
else:
    print(colored('Tp Test Failed, Tp = ' + str(Tp) + ', Tp_t = ' + str(Tp_t), 'red'))

# Test Dp
if(np.abs(Dp-Dp_t) <= precision ):
    print(colored('======== Test Dp Passed ========', 'green'))
else:
    print(colored('Dp Test Failed, Dp = ' + str(Dp) + ', Dp_t = ' + str(Dp_t), 'red'))

# Test E
if(np.abs(np.linalg.norm(E)-np.linalg.norm(E_t)) <= precision ):
    print(colored('======== Test E Passed ========', 'green'))
else:
    print(colored('E Test Failed, norm(E) = ' + str(np.linalg.norm(E)) + ', norm(E_t) = ' + str(np.linalg.norm(E_t)), 'red'))

# Test f
if(np.abs(np.linalg.norm(f)-np.linalg.norm(f_t)) <= precision ):
    print(colored('======== Test f Passed ========', 'green'))
else:
    print(colored('f Test Failed, norm(f) = ' + str(np.linalg.norm(f)) + ', norm(f_t) = ' + str(np.linalg.norm(f_t)), 'red'))

# Test a1
if(np.abs(np.linalg.norm(a1)-np.linalg.norm(a1_t)) <= precision ):
    print(colored('======== Test a1 Passed ========', 'green'))
else:
    print(colored('a1 Test Failed, norm(a1) = ' + str(np.linalg.norm(a1)) + ', norm(a1_t) = ' + str(np.linalg.norm(a1_t)), 'red'))

# Test b1
if(np.abs(np.linalg.norm(b1)-np.linalg.norm(b1_t)) <= precision ):
    print(colored('======== Test b1 Passed ========', 'green'))
else:
    print(colored('b1 Test Failed, norm(b1) = ' + str(np.linalg.norm(b1)) + ', norm(b1_t) = ' + str(np.linalg.norm(b1_t)), 'red'))

# Test a2
if(np.abs(np.linalg.norm(a2)-np.linalg.norm(a2_t)) <= precision ):
    print(colored('======== Test a2 Passed ========', 'green'))
else:
    print(colored('a2 Test Failed, norm(a2) = ' + str(np.linalg.norm(a2)) + ', norm(a2_t) = ' + str(np.linalg.norm(a2_t)), 'red'))

# Test b2
if(np.abs(np.linalg.norm(b2)-np.linalg.norm(b2_t)) <= precision ):
    print(colored('======== Test b2 Passed ========', 'green'))
else:
    print(colored('b2 Test Failed, norm(b2) = ' + str(np.linalg.norm(b2)) + ', norm(b2_t) = ' + str(np.linalg.norm(b2_t)), 'red'))

