#! /usr/bin/python2.7
import numpy as np

testArray = np.array([1.2830729153979296e+294, -1.57376965e-03, 4.82011728e-08, 1.9289677e-12])
testArray2 = np.array([9.9984930e+03, -9.57376965e-03, 0.82011728e-08, 1.92894253e-12])

# float_formatter = "{:.5f}".format
# np.set_printoptions(formatter={'float_kind':float_formatter})
#np.set_printoptions(precision=5)
#np.set_printoptions(suppress=True)
#testArray = np.around(testArray,decimals=3)\


def myRound(value, N):
    exponent = np.ceil(np.log10(value))
    return 10**exponent*np.round(value*10**(-exponent),N)

def myRound2(value, N):
    value = np.asarray(value).copy()
    zero_mask = (value == 0)
    value[zero_mask] = 1.0
    sign_mask = (value < 0)
    value[sign_mask] *= -1
    exponent = np.ceil(np.log10(value))
    result = 10**exponent*np.round(value*10**(-exponent), N)
    result[sign_mask] *= -1
    result[zero_mask] = 0.0
    return result


#testArray.round(decimals=3, out=testArray)
#test = myRound2(testArray,3)
#rounded = [round(num, 4) for num in testArray]
#arrayRound = np.round(testArray,5)
#listArray = list(arrayRound)
for i in testArray:
    if i > 18446744073709551615:
        i = 999.0000
    print(i)

testArray = np.where(testArray>=18446744073709551615, 999.00000, testArray)
np.set_printoptions(formatter={'float_kind':'{:.5f}'.format})
np.set_printoptions(formatter={'float_kind':'{:.2e}'.format})

#testArray = ['{:.5f}'.format(item) for item in testArray]

#print ('Test Array', test)
#print ('Saved', newThing)
print(('Test Array 2', testArray))