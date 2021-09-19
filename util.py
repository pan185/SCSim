from scipy.stats import bernoulli
import numpy as np
import sys
from pylfsr import LFSR
import trng

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

def gen_TRNG_bistream(length, mode='TRNG', entropy_sources_list=None):
    if length <= 0:
        raise Exception("TRNG bistream length should be greater than 0!")
    if mode == 'TRNG':
        p = 0.5
        X = bernoulli(p) # Fair bernoulli
        bitstream = X.rvs(length)
        return bitstream

    elif mode == 'dff':
        bitstream = np.zeros(length) 

        bitstream = [0 for i in range(length)] 
        for i in range(length): 
            if i % 2 == 1: bitstream[i] = 1
        return bitstream

    elif mode == 'lfsr':
        bitwidth = int(np.log2(length))
        polylist = LFSR().get_fpolyList(m=bitwidth)
        poly = polylist[np.random.randint(0, len(polylist), 1)[0]] # random seed, random fpoly

        # Using random state is bad because 0 is also included
        state = bin(np.random.randint(1, 2**bitwidth, 1)[0])
        state = state[2::]
        state = state.zfill(bitwidth)
        state = list(state)
        for i in range(bitwidth):
            state[i] = int(state[i])

        L = LFSR(fpoly=poly,initstate = state)
        #seq = L.runFullCycle()
        seq = L.runKCycle(length)
        assert(length == len(seq))
        #result = L.test_properties(verbose=2)
        return seq
    elif mode == 'QUAC':
        if entropy_sources_list == None: 
            raise Exception('entropy_sources_list cannot be None')
        return entropy_sources_list[0].get_256_bit_random_bitstream()

    else:
        raise Exception(f"Mode {mode} not found!")

def get_lfsr_seq(bitwidth=8):
    polylist = LFSR().get_fpolyList(m=bitwidth)
    poly = polylist[np.random.randint(0, len(polylist), 1)[0]]

    # Using random state is bad because 0 is also included
    state = bin(np.random.randint(1, 2**bitwidth, 1)[0])
    state = state[2::]
    state = state.zfill(bitwidth)
    state = list(state)
    for i in range(bitwidth):
        state[i] = int(state[i])

    L = LFSR(fpoly=poly,initstate = state)
    lfsr_seq = []
    for i in range(2**bitwidth):
        value = 0
        for j in range(bitwidth):
            value = value + L.state[j]*2**(bitwidth-1-j)
        lfsr_seq.append(value)
        L.next()
    return lfsr_seq

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
        # ct = 0
        # for i in rep:
        #     if i == '1' or i == 1: ct += 1
        # return ct
        rep = np.array(rep)
        #num_ones = (rep == 1 or rep == '1').sum()
        return rep.sum()
    
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