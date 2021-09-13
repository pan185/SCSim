import numpy as np
from pylfsr import LFSR
import matplotlib.pyplot as plt

def get_lfsr_seq(bitwidth=8):
    polylist = LFSR().get_fpolyList(m=bitwidth)
    poly = polylist[np.random.randint(0, len(polylist), 1)[0]]
    L = LFSR(fpoly=poly,initstate ='random')
    lfsr_seq = []
    for i in range(2**bitwidth):
        value = 0
        for j in range(bitwidth):
            value = value + L.state[j]*2**(bitwidth-1-j)
        lfsr_seq.append(value)
        L.next()
    return lfsr_seq

def get_rand_bs(length=256):
    bitwidth = int(np.log2(length))
    polylist = LFSR().get_fpolyList(m=bitwidth)
    poly = polylist[np.random.randint(0, len(polylist), 1)[0]]
    L = LFSR(fpoly=poly,initstate ='random')
    #seq = L.runFullCycle()
    seq = L.runKCycle(length)
    assert(length == len(seq))
    #result = L.test_properties(verbose=2)
    return seq

print((get_rand_bs(256)))