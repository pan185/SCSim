from scipy.stats import bernoulli
import numpy as np
import sys
from pylfsr import LFSR

class global_vars:
    def __init__(self, prec=None, len=None, iter=None):
        if prec != None: self.PRECISION_BITS = prec
        else: self.PRECISION_BITS = 8

        if len != None: self.TRNG_BITSTREAM_LENGTH = len
        else: self.TRNG_BITSTREAM_LENGTH = 256

        if iter != None: self.ITER = iter
        else: self.ITER = 100

class colorText:
    CRED = '\033[91m'
    CEND = '\033[0m'
    CGREEN = '\033[92m'
    CBLUE = '\033[94m'
    CCYAN = '\033[96m'

def gen_TRNG_bistream(length, mode='TRNG'):
    if length <= 0:
        raise Exception("TRNG bistream length should be greater than 0!")
    if mode == 'TRNG':
        p = 0.5
        X = bernoulli(p) # Fair bernoulli
        bitstream = X.rvs(length)
        return bitstream

    elif mode == 'dff':
        bitstream = [0] * length
        for i in range(length): 
            if i % 2 == 1: bitstream[i] = 1
        return bitstream

    elif mode == 'lfsr':
        bitwidth = int(np.log2(length))
        polylist = LFSR().get_fpolyList(m=bitwidth)
        poly = polylist[np.random.randint(0, len(polylist), 1)[0]]
        L = LFSR(fpoly=poly,initstate ='random')
        #seq = L.runFullCycle()
        seq = L.runKCycle(length)
        assert(length == len(seq))
        #result = L.test_properties(verbose=2)
        return seq

    else:
        raise Exception(f"Mode {mode} not found!")

class Bitstream:
    """
    Get bistream result from ANDing n bitstreams
    """
    def get_anded_bistream(n, globalVars):
        if n <= 0:
            raise Exception("Cannot performance AND op on zero or less bistreams")
        
        res = gen_TRNG_bistream(globalVars.TRNG_BITSTREAM_LENGTH)
        if n == 0 or n == 1:
            return res
        
        for x in range(n-1):
            new_bs = gen_TRNG_bistream(globalVars.TRNG_BITSTREAM_LENGTH)
            res = np.bitwise_and(res, new_bs)
        return res

    def get_ored_bistream(bs1, bs2):
        return np.bitwise_or(bs1, bs2)
    
    def count_num_1s(rep):
        ct = 0
        for i in rep:
            if i == '1' or i == 1: ct += 1
        return ct
    
    def get_inverse(arr):
        isString = isinstance(arr, str)
        if isString:
            new_arr = []
            arr = list(arr)
            for x in arr:
                if x == '1': new_arr.append('0')
                elif x == '0': new_arr.append('1')
                else: sys.exit(f'Error: input string to inverter has unexpected bit {x}!')
            new_arr = ''.join(new_arr)
            return new_arr
        else:
            new_arr = []
            for x in arr:
                if x == 1: new_arr.append(0)
                elif x == 0: new_arr.append(1)
                else: sys.exit(f'Error: input string to inverter has unexpected bit {x}!')
            return new_arr