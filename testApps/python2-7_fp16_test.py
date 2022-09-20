
from __future__ import division # true division
import struct

def usigned16_from_hex(hex):
    """convert hex to unsigned 16-bit int (short)"""
    return struct.unpack('<H',hex)[0] # (returned as first index of tuple)

def float_from_unsigned16(n):
    """
    Read IEEE 754 half-precision float
    source: https://gist.github.com/zed/59a413ae2ed4141d2037
    """
    assert 0 <= n < 2**16
    sign = n >> 15
    exp = (n >> 10) & 0b011111
    fraction = n & (2**10 - 1)
    if exp == 0:
        if fraction == 0:
            return -0.0 if sign else 0.0
        else:
            return (-1)**sign * fraction / 2**10 * 2**(-14)  # subnormal
    elif exp == 0b11111:
        if fraction == 0:
            return float('-inf') if sign else float('inf')
        else:
            return float('nan')
    return (-1)**sign * (1 + fraction / 2**10) * 2**(exp - 15)

TX_fname = './testApps/microSWIFT019_TX_12Sep2022_165147UTC.dat'

with open(TX_fname, mode='rb') as file: 
    fileContent = file.read()

"""in python 3.7"""
# Hs = struct.unpack('e',fileContent[5:7]) # Hs = 0.004505157470703125
# Tp = struct.unpack('e',fileContent[7:9]) # Hs = 12.484375
# Voltage = struct.unpack('e',fileContent[321:323]) # Voltage = 0.0

"""in python 2.7"""
# read sig wave height hex (b'\x9d\x1c') as unsigned16 (= 7325):
u16 = usigned16_from_hex(fileContent[5:7]) 
print('unsigned16: ' + str(u16))

# read unsigned 16 as 16-bit floats:
Hs = float_from_unsigned16(u16) # = 0.0045051574707

# Test Tp and Voltage:
Tp = float_from_unsigned16(usigned16_from_hex(fileContent[7:9])) # = 12.484375
Voltage = float_from_unsigned16(usigned16_from_hex(fileContent[321:323])) # = 0.0

print('Hs: ' + str(Hs))
print('Tp:' + str(Tp))
print('Voltage:' + str(Voltage))

