from scipy.stats import bernoulli
import util
import hashlib
import numpy as np
import timeit
import matplotlib.pyplot as plt



class DRAMEntropyBlock:
    def __init__(self, bitline_ct, bias_constant=0, post_proc_scheme = 'SHA256'):
        small = 0.0013966171252525419
        self.bitline_ct = bitline_ct
        self.bias_constant = bias_constant
        self.post_proc_scheme = post_proc_scheme

        self.bitline_rv_arr = []
        for i in range(int(self.bitline_ct)+1):
            self.bitline_rv_arr.append(bernoulli(small))
        
        print('Done constructing bitline model.')

    def get_256_bit_random_bitstream(self):
        entropy_blk_bs = [int(rv.rvs(1)) for rv in self.bitline_rv_arr]
        # for rv in self.bitline_rv_arr:
        #     outcome = rv.rvs(1)
        #     entropy_blk_bs.append(int(outcome))
        #print(entropy_blk_bs)
        print('Done generating a entropy block bs.')
        
        # freq_before = util.Bitstream.count_num_1s(entropy_blk_bs)/len(entropy_blk_bs)
        # print(util.colorText.CRED+f'Freq before processing: {freq_before}'+util.colorText.CEND)
        ##########################
        # Post-processing 
        ##########################
        if self.post_proc_scheme == 'SHA256':
            hex_post = hashlib.sha256(str(entropy_blk_bs).encode('utf-8')).hexdigest()
            bs_post = bin(int(hex_post, 16))[2:].zfill(256)
            #bs_post = bs_post[2:]
            bs_post = list(bs_post)
            #for i in range(len(bs_post)): bs_post[i] = int(bs_post[i])
            bs_post = [int(i) for i in bs_post]
            #bs_post = bs_post.astype(int)
            #print(bs_post)
            # freq_post = util.Bitstream.count_num_1s(bs_post)/len(bs_post)
            # print(util.colorText.CRED+f'Freq post processing: {freq_post}'+util.colorText.CEND)
            return bs_post
        elif self.post_proc_scheme == 'VNC':
            first_bits = entropy_blk_bs[::2]
            second_bits = entropy_blk_bs[1::2]
            bs_post = []
            for i in range(len(second_bits)):
                if first_bits[i] == 1 and second_bits[i] == 0:
                    bs_post.append(1)
                elif first_bits[i] == 0 and second_bits[i] == 1:
                    bs_post.append(0)
            return bs_post
        else:
            raise Exception('Unknown post processing scheme!')


def test_SHA256():
    SEGMENT_ENTROPY = 1000 # Use a relatively low number in QUAC-TRNG paper
    SEGMENT_BITLINE_CT = 64 * (2**10) # per 64K bitlines per row
    BITLINE_ENTROPY_AVG = SEGMENT_ENTROPY / SEGMENT_BITLINE_CT
    ENTROPYBLK_BITLINE_CT_AVG = 256/BITLINE_ENTROPY_AVG
    SIB_AVG = SEGMENT_BITLINE_CT/ENTROPYBLK_BITLINE_CT_AVG

    BIAS_CONSTANT = 0.9

    print('Average bitline entropy: ', BITLINE_ENTROPY_AVG)
    print(f'256-bit entropy block roughly needs {ENTROPYBLK_BITLINE_CT_AVG} bitlines')
    print(f'Number of 256-bit entropy blocks per segment/row: {SIB_AVG}')

    entropy_block_instance = DRAMEntropyBlock(ENTROPYBLK_BITLINE_CT_AVG, BIAS_CONSTANT, 'SHA256')
    A1=entropy_block_instance.get_256_bit_random_bitstream()
    A2=entropy_block_instance.get_256_bit_random_bitstream()
    A3=entropy_block_instance.get_256_bit_random_bitstream()
    A4=entropy_block_instance.get_256_bit_random_bitstream()
    B1 = A1
    B2 = np.bitwise_and(A1, util.Bitstream.get_inverse(A2))
    B3 = np.bitwise_and(np.bitwise_and(A1, util.Bitstream.get_inverse(A2)), util.Bitstream.get_inverse(A3))
    B4 = np.bitwise_and(np.bitwise_and(np.bitwise_and(A1, util.Bitstream.get_inverse(A2)), util.Bitstream.get_inverse(A3)), util.Bitstream.get_inverse(A4))
    print(util.Bitstream.count_num_1s(B1)/256)
    print(util.Bitstream.count_num_1s(B2)/256)
    print(util.Bitstream.count_num_1s(B3)/256)
    print(util.Bitstream.count_num_1s(B4)/256)

def test_SHA256_H():
    SEGMENT_ENTROPY = 1000 # Use a relatively low number in QUAC-TRNG paper
    SEGMENT_BITLINE_CT = 64 * (2**10) # per 64K bitlines per row
    BITLINE_ENTROPY_AVG = SEGMENT_ENTROPY / SEGMENT_BITLINE_CT
    ENTROPYBLK_BITLINE_CT_AVG = 256/BITLINE_ENTROPY_AVG
    SIB_AVG = SEGMENT_BITLINE_CT/ENTROPYBLK_BITLINE_CT_AVG

    BIAS_CONSTANT = 0.9

    print('Average bitline entropy: ', BITLINE_ENTROPY_AVG)
    print(f'256-bit entropy block roughly needs {ENTROPYBLK_BITLINE_CT_AVG} bitlines')
    print(f'Number of 256-bit entropy blocks per segment/row: {SIB_AVG}')

    entropy_block_instance = DRAMEntropyBlock(ENTROPYBLK_BITLINE_CT_AVG, BIAS_CONSTANT, 'SHA256')
    A = []
    ct = 1000
    for i in range(ct):
        A.append(entropy_block_instance.get_256_bit_random_bitstream())
    assert len(A[0]) == 256
    p = [sum(x)/ct for x in zip(*A)]
    H = [get_H(p[i]) for i in range(256)]
    print(H)
    plt.plot(range(256), H)
    plt.show()
def get_H(p):
    return -1 * (p*np.log2(p) + (1-p)*np.log(1-p))
def test_VNC():
    SEGMENT_BITLINE_CT = 64 * (2**10) # per 64K bitlines per row
    entropy_block_instance = DRAMEntropyBlock(SEGMENT_BITLINE_CT, 0, 'VNC')
    A = []
    B = []
    min_len = SEGMENT_BITLINE_CT
    for i in range(4): 
        Ai = entropy_block_instance.get_256_bit_random_bitstream()# Note not necessarily 256 bit
        min_len = min(min_len, len(Ai))
        print(min_len)
        A.append(Ai[0:min_len])
    print('Compression rate % = ',min_len/SEGMENT_BITLINE_CT*100)
    for i in range(4):
        Bi = Ai[0:min_len]
        for j in range(i): Bi = np.bitwise_and(Bi, np.bitwise_not(A[j][0:min_len]))
        B.append(Bi)
        print('B value = ',util.Bitstream.count_num_1s(Bi[0:min_len])/len(Bi[0:min_len]))

def main():
    #test_SHA256()
    test_SHA256_H()
    #test_VNC()
if __name__ == "__main__":
    main()
