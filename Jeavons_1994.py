import numpy as np
import matplotlib.pyplot as plt
import gc
import argparse
import sys
sys.path.append('/Users/zhewenpan/Repo/SCSim')
import util
import torch
import trng

SEGMENT_ENTROPY = 1000 # Use a relatively low number in QUAC-TRNG paper
SEGMENT_BITLINE_CT = 64 * (2**10) # per 64K bitlines per row
BITLINE_ENTROPY_AVG = SEGMENT_ENTROPY / SEGMENT_BITLINE_CT
ENTROPYBLK_BITLINE_CT_AVG = 256/BITLINE_ENTROPY_AVG
SIB_AVG = SEGMENT_BITLINE_CT/ENTROPYBLK_BITLINE_CT_AVG
BIAS_CONSTANT = 0.9

class Module:
    # index = 0
    # r_i = []
    # y_i = -999
    # x_i = -555
    # y_o = -333

    def __init__(self, index, x, globalVar, mode, entropy_sources):
        self.index = index
        self.r_i = util.gen_TRNG_bistream(globalVar.PRECISION_BITS + globalVar.TRNG_BITSTREAM_LENGTH, mode, entropy_sources)

        if (self.index == 0): self.y_i = 0
        else: self.y_i = -999

        x_assign = x[globalVar.PRECISION_BITS - 1 - self.index] # MSB should be on the right
        x_assign = int(x_assign)
        self.x_i = x_assign

        self.y_o = -333

        # TODO: Remove debugging msg
        # print(colorText.CCYAN+f'Called Module Init'+colorText.CEND)
        # self.print_info(0)
    
    def set_y_i(self, val):
        self.y_i = val

    def calculate_y_o(self, r_index, verbose=False, scheme='majority'):
        if self.y_i < 0:
            # raise Exception(f'Bad initialization! X = {self.x_i}, Y = {self.y_i}')
            if verbose: print(util.colorText.CRED + f'Warning: Calculating y_o with bad X initialization! Y = {self.y_i}' + util.colorText.CEND)
            self.y_o = -99999999
        elif self.x_i != 0 and self.x_i != 1: 
            # raise Exception(f'Bad initialization! X = {self.x_i}, Y = {self.y_i}')
            if verbose: print(util.colorText.CRED + f'Warning: Calculating y_o with bad Y initialization! X = {self.x_i}' + util.colorText.CEND)
            self.y_o = -99999999
        else:
            if scheme == 'majority':
                self.y_o = (self.x_i & self.y_i) | (self.x_i & self.r_i[r_index]) | (self.y_i & self.r_i[r_index])
            elif scheme == 'two_min_term':
                self.y_o = (self.x_i & self.r_i[r_index]) | (self.y_i & self.r_i[r_index])
            elif scheme == 'other':
                self.y_o = (self.x_i & self.y_i) | (self.x_i & self.r_i[r_index]) | (self.y_i & self.r_i[r_index] & (~self.x_i))
            else:
                sys.exit(util.colorText.CRED + f'Error: Unknown scheme name {scheme}' + util.colorText.CEND)
    
    def print_info(self, cycle=None):
        if cycle == None:
            print(f'- - - - - M[{self.index}] - - - - - (init time)')
            print(f'x = {self.x_i}\ny = {self.y_i}')
            print(f'r = {self.r_i}\ny_o = {self.y_o}')
            print('')
        else:
            print(f'---------- M[{self.index}] ----------')
            print(f'x = {self.x_i}\ny = {self.y_i}')
            print(f'r[{cycle}] = {self.r_i[cycle]}\ny_o = {self.y_o}')
            print('')
    
    def delete_M(self):
        del self
        


class Structure:
    # M = []
    # len = -1
    # x = []
    # sn = [-1] * (TRNG_BITSTREAM_LENGTH + PRECISION_BITS)

    def __init__(self, len, x, globalVar, mode):
        self.len = len
        self.x = x
        
        self.M = []
        for i in range(len):
            m_instance = Module(i, x, globalVar, mode)
            self.M.append(m_instance)

        self.sn = [-1] * (globalVar.TRNG_BITSTREAM_LENGTH + globalVar.PRECISION_BITS)

        # TODO: Remove debugging msg
        # print(colorText.CBLUE+f'Called Structure Init'+colorText.CEND)
        # self.print_info()

    def print_info(self, cycle=None):
        if cycle == None:
            print(f'======= Structure({self.len}) at init time ===========')
            print(f'x = {self.x}\nsn = {self.sn}')

            for i in range(self.len):
                self.M[i].print_info()
        else:
            print(f'******** Structure({self.len}) at cycle {cycle} ***********')
            print(f'x = {self.x}\nsn[{cycle}] = {self.sn[cycle]}')

            for i in range(self.len):
                self.M[i].print_info(cycle)
        

    
    def propagate_y_value(self, cur_cycle, verbose=False, scheme='majority'):
        # sn snarfs valid value from M[len-1]
        sn_snarf = self.M[self.len-1].y_o
        if sn_snarf >= 0:
            self.sn[cur_cycle] = sn_snarf

        for i in range(self.len):
            if i == 0: # M0 has nothing to snarf
                self.M[0].calculate_y_o(cur_cycle, verbose, scheme) # calculate y_o for M0
            else:
                self.M[i].calculate_y_o(cur_cycle, verbose, scheme)
                # Snarf value from previous module
                y_read_out = self.M[i-1].y_o
                self.M[i].set_y_i(y_read_out)
        
        # TODO: take out when stop debugging
        #if cur_cycle < 6: self.print_info(cur_cycle)
    def get_sn(self):
        return self.sn

    def post_processing_yo(self, globalVar):
        bad_ct = 0
        one_ct = 0
        for i in self.sn:
            if i != 1 and i != 0:
                bad_ct += 1
            elif i == 1:
                one_ct += 1

        if bad_ct != globalVar.PRECISION_BITS: raise Exception(f'Something went wrong! bad_ct={bad_ct}')

        trimed_sn = self.sn[globalVar.PRECISION_BITS:]
        self.sn = trimed_sn
        # TODO: remove debug msg
        #print(f'#1={one_ct}, #bad={bad_ct}, len={len(self.sn)}')

        bs_freq = one_ct / (len(self.sn) - bad_ct)
        return bs_freq
    
    def delete_structure(self):
        for i in range(self.len):
            self.M[i].delete_M()

class SNG(torch.nn.Module):
    """
    
    """
    def __init__(self,
                 globalVar,
                 scheme='majority',
                 mode='TRNG'):
        super(SNG, self).__init__()
        self.scheme = scheme
        self.mode = mode
        self.globalVar=globalVar

    def forward(self, num_decimal, entropy_sources):
        ########################
        # Compute binary number
        ########################
        if num_decimal > 2**self.globalVar.PRECISION_BITS: 
            raise Exception(f"Specified decimal value {num_decimal} is too large. Max is {2**self.globalVar.PRECISION_BITS - 1}.")
        expected_freq = num_decimal/2**self.globalVar.PRECISION_BITS

        num_binary = bin(num_decimal)
        num_binary = num_binary[2:]
        if len(num_binary) < self.globalVar.PRECISION_BITS:
            num_binary = num_binary.zfill(self.globalVar.PRECISION_BITS)
        
        ###############################
        # Compute error based on scheme
        ###############################`
        if self.scheme == 'majority' or self.scheme == 'two_min_term' or self.scheme == "other":
            S = Structure(self.globalVar.PRECISION_BITS, num_binary, self.globalVar, self.mode)
            for cyc in range(self.globalVar.PRECISION_BITS + self.globalVar.TRNG_BITSTREAM_LENGTH):
                S.propagate_y_value(cyc, False, self.scheme)
            S.post_processing_yo(self.globalVar)
            sn = S.get_sn()
            
            return sn
        if 'plus_multiply' in self.scheme:
            
            # inverse binary if needed
            inverse = False
            if self.scheme == 'plus_multiply_inverse':
                if num_binary[0] == '1' and util.Bitstream.count_num_1s(num_binary) != 1:
                    # any binary greater than 0.5, inverse it
                    inverse = True
                    num_binary = util.Bitstream.get_inverse(num_binary)

            found_first = False
            index = 0

            num_mult_op = 0
            num_plus_op = 0

            bs_res = ['0'] * self.globalVar.TRNG_BITSTREAM_LENGTH
            bs_res = ''.join(bs_res)

            for bit in num_binary:
                if bit == '1':
                    if found_first: # If not processing the first 1 in fixed point representation
                        bs_new = util.Bitstream.get_anded_bistream(index+1, self.globalVar)
                        num_mult_op += (index + 1)
                        bs_res = util.Bitstream.get_ored_bistream(bs_res, bs_new)
                        num_plus_op += 1
                    else:
                        bs_res = util.Bitstream.get_anded_bistream(index+1, self.globalVar)
                        num_mult_op += index + 1
                    found_first = True
                index += 1
            
            # if inverted then inverse it back
            if inverse:
                bs_res = util.Bitstream.get_inverse(bs_res)

            return bs_res
        if self.scheme =='gaines':
            A = []
            for i in range(self.globalVar.PRECISION_BITS):
                A.append(util.gen_TRNG_bistream(self.globalVar.TRNG_BITSTREAM_LENGTH, self.mode, entropy_sources))
            B = []
            for j in range(self.globalVar.PRECISION_BITS):
                Bj = A[j]
                for i in range(j):
                    if j != 0:
                        for t in range(len(A[i])): Bj[t] &= ~A[i][t]
                B.append(Bj)
            
            stream = [0] * self.globalVar.TRNG_BITSTREAM_LENGTH
            for index in range(len(num_binary)):
                if num_binary[index] == '1' or num_binary[index] == 1:
                    for i in range(self.globalVar.TRNG_BITSTREAM_LENGTH):
                        stream[i] = stream[i] | B[index][i]
            
            return stream
        if self.scheme == 'comparator':
            if 2**self.globalVar.PRECISION_BITS != self.globalVar.TRNG_BITSTREAM_LENGTH:
                raise Exception('Only full length lfsr+comparator is supported so far!')
            if self.mode == 'lfsr':
                lfsr_sequence = util.get_lfsr_seq(8)
            elif self.mode == 'TRNG':
                lfsr_sequence = []
                for i in range(self.globalVar.TRNG_BITSTREAM_LENGTH):
                    trng_bs = util.gen_TRNG_bistream(self.globalVar.PRECISION_BITS, 'TRNG')
                    index_val = self.globalVar.PRECISION_BITS-1
                    decimal_val = 0
                    for j in trng_bs:
                        if j == '1' or j == 1: decimal_val += 2**index_val
                        index_val -= 1

                    lfsr_sequence.append(decimal_val)
            else:
                raise Exception(util.colorText.CRED+ f"Warning: using comparator scheme but {self.mode} mode!"+util.colorText.CEND)
            stochastic_bs = [0] * (2**self.globalVar.PRECISION_BITS)
            index = 0
            for i in lfsr_sequence:
                if num_decimal > i: stochastic_bs[index] = 1
                index += 1
            return stochastic_bs

        else:
            sys.exit(util.colorText.CRED + f'Error: unknown scheme {self.scheme}!' + util.colorText.CEND)

def compute_err(num_decimal, globalVar, verbose=False, scheme='majority', mode='TRNG', entropy_sources=None):
    ########################
    # Compute binary number
    ########################
    if num_decimal > 2**globalVar.PRECISION_BITS: 
        raise Exception(f"Specified decimal value {num_decimal} is too large. Max is {2**globalVar.PRECISION_BITS - 1}.")
    expected_freq = num_decimal/2**globalVar.PRECISION_BITS

    num_binary = bin(num_decimal)
    num_binary = num_binary[2:]
    if len(num_binary) < globalVar.PRECISION_BITS:
        num_binary = num_binary.zfill(globalVar.PRECISION_BITS)
    
    ###############################
    # Compute error based on scheme
    ###############################
    if scheme == 'majority' or scheme == 'two_min_term' or scheme == "other":
        S = Structure(globalVar.PRECISION_BITS, num_binary, globalVar, mode)
        for cyc in range(globalVar.PRECISION_BITS + globalVar.TRNG_BITSTREAM_LENGTH):
            S.propagate_y_value(cyc, verbose, scheme)
        freq = S.post_processing_yo(globalVar)
        err = abs(expected_freq - freq)
        if verbose: print(util.colorText.CGREEN + f'Result: {freq}, Expecting: {expected_freq}, err: {err}' + util.colorText.CEND)
        
        S.delete_structure
        del S
        gc.collect()

        return err, None, None
    if 'plus_multiply' in scheme:
        
        # inverse binary if needed
        inverse = False
        if scheme == 'plus_multiply_inverse':
            if num_binary[0] == '1' and util.Bitstream.count_num_1s(num_binary) != 1:
                # any binary greater than 0.5, inverse it
                inverse = True
                num_binary = util.Bitstream.get_inverse(num_binary)

        found_first = False
        index = 0

        num_mult_op = 0
        num_plus_op = 0

        bs_res = ['0'] * globalVar.TRNG_BITSTREAM_LENGTH
        bs_res = ''.join(bs_res)

        for bit in num_binary:
            if bit == '1':
                if found_first: # If not processing the first 1 in fixed point representation
                    bs_new = util.Bitstream.get_anded_bistream(index+1, globalVar)
                    num_mult_op += (index + 1)
                    bs_res = util.Bitstream.get_ored_bistream(bs_res, bs_new)
                    num_plus_op += 1
                else:
                    bs_res = util.Bitstream.get_anded_bistream(index+1, globalVar)
                    num_mult_op += index + 1
                found_first = True
            index += 1
        
        # if inverted then inverse it back
        if inverse:
            bs_res = util.Bitstream.get_inverse(bs_res)

        num1 = util.Bitstream.count_num_1s(bs_res)
        freq = num1 / globalVar.TRNG_BITSTREAM_LENGTH
        err = abs(expected_freq - freq)
        if verbose: print(util.colorText.CGREEN + f'Result: {freq}, Expecting: {expected_freq}, err: {err}         (mult={num_mult_op}, plus={num_plus_op})' + util.colorText.CEND)
        return err, num_mult_op, num_plus_op
    if scheme =='gaines':
        A = []
        for i in range(globalVar.PRECISION_BITS):
            A.append(util.gen_TRNG_bistream(globalVar.TRNG_BITSTREAM_LENGTH, mode, entropy_sources))
        B = []
        for j in range(globalVar.PRECISION_BITS):
            Bj = A[j]
            for i in range(j):
                if j != 0:
                    for t in range(len(A[i])): Bj[t] &= ~A[i][t]
            B.append(Bj)
        
        print(len(B))
        print(len(B[0]))
        stream = [0] * globalVar.TRNG_BITSTREAM_LENGTH
        for index in range(len(num_binary)):
            if num_binary[index] == '1' or num_binary[index] == 1:
                for i in range(globalVar.TRNG_BITSTREAM_LENGTH):
                    stream[i] = stream[i] | B[index][i]
        
        num1 = util.Bitstream.count_num_1s(stream)
        freq = num1 / globalVar.TRNG_BITSTREAM_LENGTH
        err = abs(expected_freq - freq)
        if verbose: print(util.colorText.CGREEN + f'Result: {freq}, Expecting: {expected_freq}, err: {err}' + util.colorText.CEND)
        return err, None, None
    if scheme == 'comparator':
        if 2**globalVar.PRECISION_BITS != globalVar.TRNG_BITSTREAM_LENGTH:
            raise Exception('Only full length lfsr+comparator is supported so far!')
        if mode == 'lfsr':
            lfsr_sequence = util.get_lfsr_seq(8)
        elif mode == 'TRNG':
            lfsr_sequence = []
            for i in range(globalVar.TRNG_BITSTREAM_LENGTH):
                trng_bs = util.gen_TRNG_bistream(globalVar.PRECISION_BITS, 'TRNG')
                index_val = globalVar.PRECISION_BITS-1
                decimal_val = 0
                for j in trng_bs:
                    if j == '1' or j == 1: decimal_val += 2**index_val
                    index_val -= 1

                lfsr_sequence.append(decimal_val)
        else:
            raise Exception(util.colorText.CRED+ f"Warning: using comparator scheme but {mode} mode!"+util.colorText.CEND)
        stochastic_bs = [0] * (2**globalVar.PRECISION_BITS)
        index = 0
        for i in lfsr_sequence:
            if num_decimal > i: stochastic_bs[index] = 1
            index += 1

        num1 = util.Bitstream.count_num_1s(stochastic_bs)
        freq = num1 / globalVar.TRNG_BITSTREAM_LENGTH
        err = abs(expected_freq - freq)
        if verbose: 
            if err > 0.1: 
                color_string = util.colorText.CRED
                print(color_string + f'lfsr={lfsr_sequence}' + util.colorText.CEND)
            else: 
                color_string = util.colorText.CGREEN
                if err != 0: print(color_string + f'lfsr={lfsr_sequence}' + util.colorText.CEND)
            print(color_string + f'Result: {freq}, Expecting: {expected_freq}, err: {err}' + util.colorText.CEND)

        return err, None, None

    else:
        sys.exit(util.colorText.CRED + f'Error: unknown scheme {scheme}!' + util.colorText.CEND)

def dump_stats(avg_err, max_err, scheme, mode):
    name1 = f"result/Jeavons/scaling_analysis/avg_err_{scheme}_{mode}.txt"
    name2 = f"result/Jeavons/scaling_analysis/max_err_{scheme}_{mode}.txt"
    f = open(name1, "a")
    f.write(str(avg_err)+'\n')
    f.close()

    f = open(name2, "a")
    f.write(str(max_err)+'\n')
    f.close()
    print(f'Dumped stats at {name1} and {name2}')

def dump_vec(arr, scheme, cycle, prec, mode):
    name = f"result/Jeavons/{scheme}_{prec}_M_{cycle}_cycle_{mode}_avg_err.txt"
    f = open(name, "a")
    for ele in arr:
        f.write(str(ele)+'\n')
    f.close()
    print(f'Dumped vector at {name}')

def main(raw_args=None):
    #############
    # argparse
    #############
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', default=False, action='store_true', help='Print warning msg')
    parser.add_argument('--prec', type=int, default=None, action='store', help='Set PRECISON_BITS')
    parser.add_argument('--len', type=int, default=None, action='store', help='Set TRNG_BITSTREAM_LENGTH')
    parser.add_argument('--iter', type=int, default=None, action='store', help='Set ITER')
    parser.add_argument('--scheme', type=str, default='majority', action='store', choices=['majority', 'other', 'two_min_term', 'plus_multiply', 'plus_multiply_inverse', 'gaines', 'comparator'], help='Set scheme name')
    parser.add_argument('--mode', type=str, default='TRNG', action='store', choices=['TRNG', 'dff', 'lfsr', 'QUAC'], help='Set RNG mode')
    parser.add_argument('--progress', default=False, action='store_true', help='Print progress')
    args = parser.parse_args(raw_args)

    globalVar = util.global_vars(args.prec, args.len, args.iter)

    #######################################
    # Initialize DRAM entropy source blocks
    #######################################
    entropy_sources = None
    if args.mode == 'QUAC':
        print("Start initializing DRAM source")
        entropy_sources = []
        for i in range(int(1)):
            entropy_sources.append(trng.DRAMEntropyBlock(SEGMENT_BITLINE_CT, BIAS_CONSTANT))
        print("Done initializing DRAM source")

    #############
    # Computation
    #############
    err_avg_across_ITER = [-1] * 2**globalVar.PRECISION_BITS
    nummult_avg_across_ITER = [-1] * 2**globalVar.PRECISION_BITS
    numplus_avg_across_ITER = [-1] * 2**globalVar.PRECISION_BITS

    for i in range(2**globalVar.PRECISION_BITS):
        if args.progress: print(util.colorText.CCYAN+ f'Progress {i/(2**globalVar.PRECISION_BITS)*100}%' + util.colorText.CEND)
        err_iter = [-1] * globalVar.ITER
        mult_iter = [-1] * globalVar.ITER
        plus_iter = [-1] * globalVar.ITER
        for j in range(globalVar.ITER):
            err, num_mult, num_plus = compute_err(i, globalVar, args.verbose, args.scheme, args.mode, entropy_sources)
            #print(f'mult={num_mult}, plus={num_plus}')
            err_iter[j] = err
            if 'plus_multiply' in args.scheme:
                mult_iter[j] = num_mult
                plus_iter[j] = num_plus

        
        err_avg = sum(err_iter) / len(err_iter)
        err_avg_across_ITER[i] = err_avg
        if 'plus_multiply' in args.scheme:
            mult_avg = sum(mult_iter) / len(mult_iter)
            plus_avg = sum(plus_iter) / len(plus_iter)
            nummult_avg_across_ITER[i] = mult_avg
            numplus_avg_across_ITER[i] = plus_avg

            #print(f'mult={mult_avg}, plus={plus_avg}')
            #print(f'mult={nummult_avg_across_ITER[i]}, plus={numplus_avg_across_ITER[i]}')

    overall_avg_err = sum(err_avg_across_ITER) / len(err_avg_across_ITER)
    max_err = max(err_avg_across_ITER)
    if 'plus_multiply' in args.scheme:
        overall_avg_mult = sum(nummult_avg_across_ITER) / len(nummult_avg_across_ITER)
        overall_avg_plus = sum(numplus_avg_across_ITER) / len(numplus_avg_across_ITER)
        max_mult = max(nummult_avg_across_ITER)
        max_plus = max(numplus_avg_across_ITER)
        #print(f'mult={nummult_avg_across_ITER}, plus={numplus_avg_across_ITER}')

    #############
    # Dump stats
    #############
    dump_stats(overall_avg_err, max_err, args.scheme, args.mode)

    #############
    # Visualization
    #############
    if 'plus_multiply' in args.scheme:
        fig, axs = plt.subplots(2)
        if globalVar.PRECISION_BITS >= 8:
            fig.set_size_inches(45, 12)
        else:
            fig.set_size_inches(20, 8)
        fig.suptitle(f'TRNG bitstream len = {globalVar.TRNG_BITSTREAM_LENGTH}, across {globalVar.ITER} iterations, using {args.scheme} scheme and {args.mode} RNG')
        plt.subplots_adjust(hspace = 0.4)

        x_val = np.linspace(0, 2**globalVar.PRECISION_BITS - 1, 2**globalVar.PRECISION_BITS)
        x_bin = []
        for index in range(len(x_val)): 
            bin_string = bin(int(x_val[index]))
            bin_string = bin_string[2:]
            if len(bin_string) < globalVar.PRECISION_BITS:
                bin_string = bin_string.zfill(globalVar.PRECISION_BITS)
            x_bin.append(bin_string)

        axs[0].plot(x_bin, err_avg_across_ITER, 'o-', markersize=5)
        plt.xticks(x_val, x_bin, rotation='vertical')
        axs[0].grid()
        axs[0].text(0.1, 0.5, f'avg={"{:.5f}".format(overall_avg_err)}, max={max_err}', horizontalalignment='left', verticalalignment='center', transform=axs[0].transAxes)
        axs[0].set_title("L1 Error Profile")

        axs[1].stackplot(x_bin, nummult_avg_across_ITER, numplus_avg_across_ITER, labels=['AND operations','OR operations'])# 'o-', markersize=5)
        axs[1].legend(loc="upper right")
        axs[1].grid()
        axs[1].text(0.1, 0.5, f'mult_avg={"{:.3f}".format(overall_avg_mult)}, mult_max={max_mult}\nplus_avg={"{:.3f}".format(overall_avg_plus)}, plus_max={max_plus}', horizontalalignment='left', verticalalignment='center', transform=axs[1].transAxes)
        axs[1].set_title("number of multipy (AND) and plus (OR) operations")

        plt.setp(axs[:], xlabel='Binary value x[3:0]')
        plt.setp(axs[0], ylabel='avg L1 error')
        plt.setp(axs[1], ylabel='number operations')
        plt.figtext(0, 0, f"", ha="left", fontsize=7)
        plt.savefig(f'result/Jeavons/{args.scheme}_{globalVar.PRECISION_BITS}_M_{globalVar.TRNG_BITSTREAM_LENGTH}_cycle_{args.mode}.png')
    else:
        fig, axs = plt.subplots(1)
        if globalVar.PRECISION_BITS >= 8:
            fig.set_size_inches(45, 12)
        else:
            fig.set_size_inches(20, 8)
        fig.suptitle(f'TRNG bitstream len = {globalVar.TRNG_BITSTREAM_LENGTH}, across {globalVar.ITER} iterations, using {args.scheme} module and {args.mode} RNG')
        plt.subplots_adjust(hspace = 0.4)

        x_val = np.linspace(0, 2**globalVar.PRECISION_BITS - 1, 2**globalVar.PRECISION_BITS)
        x_bin = []
        for index in range(len(x_val)): 
            bin_string = bin(int(x_val[index]))
            bin_string = bin_string[2:]
            if len(bin_string) < globalVar.PRECISION_BITS:
                bin_string = bin_string.zfill(globalVar.PRECISION_BITS)
            x_bin.append(bin_string)

        axs.plot(x_bin, err_avg_across_ITER, 'o-', markersize=5)
        plt.xticks(x_bin, x_bin, rotation='vertical')
        axs.grid()
        axs.text(0.1, 0.5, f'avg={"{:.5f}".format(overall_avg_err)}, max={max_err}', horizontalalignment='left', verticalalignment='center', transform=axs.transAxes)
        axs.set_title("L1 Error Profile")
        plt.setp(axs, xlabel=f'Binary value x[{globalVar.PRECISION_BITS-1}:0]')
        plt.setp(axs, ylabel='avg L1 error')
        plt.figtext(0, 0, f"", ha="left", fontsize=7)
        plt.savefig(f'result/Jeavons/{args.scheme}_{globalVar.PRECISION_BITS}_M_{globalVar.TRNG_BITSTREAM_LENGTH}_cycle_{args.mode}.png')
        
        
        dump_vec(err_avg_across_ITER, args.scheme, globalVar.TRNG_BITSTREAM_LENGTH, globalVar.PRECISION_BITS, args.mode)

if __name__ == "__main__":
    main()