from scipy.stats import bernoulli
import util
import hashlib
import numpy as np


class DRAMEntropyBlock:
    def __init__(self, bitline_ct, bias_constant):
        small = 0.0013966171252525419
        P = [small, 1-small]
        self.bitline_ct = bitline_ct
        self.bias_constant = bias_constant

        self.bitline_rv_arr = []
        for i in range(int(self.bitline_ct)+1):
            zero_or_one = bernoulli(self.bias_constant)
            select = zero_or_one.rvs(1)
            select = (int(select))
            p = P[select]
            self.bitline_rv_arr.append(bernoulli(p))
        print('Done constructing bitline model.')

    def get_256_bit_random_bitstream(self):
        entropy_blk_bs = []
        for rv in self.bitline_rv_arr:
            outcome = rv.rvs(1)
            entropy_blk_bs.append(int(outcome))
        #print(entropy_blk_bs)
        print('Done generating an 256-bit entropy block bs.')

        freq_before = util.Bitstream.count_num_1s(entropy_blk_bs)/len(entropy_blk_bs)
        print(util.colorText.CRED+f'Freq before processing: {freq_before}'+util.colorText.CEND)
        ##########################
        # Post-processing SHA-256
        ##########################
        hex_post = hashlib.sha256(str(entropy_blk_bs).encode('utf-8')).hexdigest()
        bs_post = bin(int(hex_post, 16))[2:].zfill(256)
        #bs_post = bs_post[2:]
        bs_post = list(bs_post)
        for i in range(len(bs_post)): bs_post[i] = int(bs_post[i])
        print(bs_post)
        freq_post = util.Bitstream.count_num_1s(bs_post)/len(bs_post)
        print(util.colorText.CRED+f'Freq post processing: {freq_post}'+util.colorText.CEND)
        return bs_post


# # Each bitline is a biased entropy source with less than 1 entropy
# # Bitlines are aggregated to form a block of 256-bit entropy block
# bitline_rv_arr = []
# for i in range(int(ENTROPYBLK_BITLINE_CT_AVG)+1):
#     zero_or_one = bernoulli(BIAS_CONSTANT)
#     select = zero_or_one.rvs(1)
#     select = (int(select))
#     p = P[select]
#     bitline_rv_arr.append(bernoulli(p))
# print('Done constructing bitline model.')

# entropy_blk_bs = []
# for rv in bitline_rv_arr:
#     outcome = rv.rvs(1)
#     entropy_blk_bs.append(int(outcome))
# #print(entropy_blk_bs)
# print('Done generating an 256-bit entropy block bs.')

# freq_before = util.Bitstream.count_num_1s(entropy_blk_bs)/len(entropy_blk_bs)
# print(util.colorText.CRED+f'Freq before processing: {freq_before}'+util.colorText.CEND)


# ##########################
# # Post-processing SHA-256
# ##########################
# hex_post = hashlib.sha256(str(entropy_blk_bs).encode('utf-8')).hexdigest()
# bs_post = bin(int(hex_post, 16))[2:].zfill(256)
# bs_post = bs_post[2:]
# #print(bs_post)
# freq_post = util.Bitstream.count_num_1s(bs_post)/len(bs_post)
# print(util.colorText.CRED+f'Freq post processing: {freq_post}'+util.colorText.CEND)

def main():
    SEGMENT_ENTROPY = 1000 # Use a relatively low number in QUAC-TRNG paper
    SEGMENT_BITLINE_CT = 64 * (2**10) # per 64K bitlines per row
    BITLINE_ENTROPY_AVG = SEGMENT_ENTROPY / SEGMENT_BITLINE_CT
    ENTROPYBLK_BITLINE_CT_AVG = 256/BITLINE_ENTROPY_AVG
    SIB_AVG = SEGMENT_BITLINE_CT/ENTROPYBLK_BITLINE_CT_AVG

    BIAS_CONSTANT = 0.9

    print('Average bitline entropy: ', BITLINE_ENTROPY_AVG)
    print(f'256-bit entropy block roughly needs {ENTROPYBLK_BITLINE_CT_AVG} bitlines')
    print(f'Number of 256-bit entropy blocks per segment/row: {SIB_AVG}')

    entropy_block_instance = DRAMEntropyBlock(ENTROPYBLK_BITLINE_CT_AVG, BIAS_CONSTANT)
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


if __name__ == "__main__":
    main()
