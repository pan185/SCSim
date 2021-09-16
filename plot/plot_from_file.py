#!/usr/bin/python
import os
import sys
import matplotlib.pyplot as plt
import argparse
import numpy as np
from scipy.stats import binom

def main(raw_args = None):
    #############
    # argparse
    #############
    parser = argparse.ArgumentParser()
    parser.add_argument('--bit', default=False, action='store_true', help='Plot error in bits')
    args = parser.parse_args(raw_args)

    pre = 'result/Jeavons/'
    gaines_TRNG = "gaines_8_M_256_cycle_TRNG_avg_err"
    gaines_lfsr = "gaines_8_M_256_cycle_lfsr_avg_err"
    gaines_quac = "gaines_8_M_256_cycle_QUAC_avg_err"
    majority_TRNG = "majority_8_M_256_cycle_TRNG_avg_err"
    majority_lfsr = "majority_8_M_256_cycle_lfsr_avg_err"
    comparator_TRNG = "comparator_8_M_256_cycle_TRNG_avg_err"
    comparator_lfsr = "comparator_8_M_256_cycle_lfsr_avg_err"
    post = '.txt'

    file_string_list = [gaines_TRNG, gaines_lfsr, gaines_quac, majority_TRNG, majority_lfsr, comparator_TRNG, comparator_lfsr]
    file_list = [pre+gaines_TRNG+post, pre+gaines_lfsr+post, pre+gaines_quac+post, pre+majority_TRNG+post, pre+majority_lfsr+post, pre+comparator_TRNG+post, pre+comparator_lfsr+post]
    err_gains_TRNG = []
    err_gaines_lfsr = []
    err_gaines_QUAC = []
    err_majority_TRNG = []
    err_majority_lfsr = []
    err_comparator_TRNG = []
    err_comparator_lfsr = []
    err_list = [err_gains_TRNG, err_gaines_lfsr, err_gaines_QUAC, err_majority_TRNG, err_majority_lfsr, err_comparator_TRNG, err_comparator_lfsr]

    index = 0
    for file_name in file_list:
        file = open(file_name, 'r')
        Lines = file.readlines()
        # Strips the newline character
        for line in Lines:
            if args.bit == True:
                err_list[index].append(float(line.strip())*256)
            else:
                err_list[index].append(float(line.strip()))
        print(len(err_list[index]))
        index += 1

    fig, axs = plt.subplots(1)
    fig.set_size_inches(45, 12)
    #axs.set_prop_cycle(color=['#9cc0e7', '#3caea3', '#f6d55c', '#9ec4c5', '#faeacb'])#'#ed553b'])
    fig.suptitle(f'TRNG bitstream len = [256], across 100 iterations, using [gaines,majority, comparator] scheme')
    plt.subplots_adjust(hspace = 0.4)
    x_val = np.linspace(0, 2**8 - 1, 2**8)
    x_bin = []
    for index in range(len(x_val)): 
        bin_string = bin(int(x_val[index]))
        bin_string = bin_string[2:]
        if len(bin_string) < 8:
            bin_string = bin_string.zfill(8)
        x_bin.append(bin_string)

    for i in range(len(err_list)):
        if 'lfsr' in file_string_list[i]: marker = '^-'
        else: marker = 'o-'
        axs.plot(x_bin, err_list[i], marker, markersize=5, label=file_string_list[i])

    ############################
    # Plot binomial distribution
    ############################
    # binom_rv = binom(256, 0.5)
    # x = range(256)
    # axs.plot(x_bin, binom_rv.pmf(x), '--', label='Binomial prob')
    ##########################
    # Plot ideal entropy
    ##########################
    # length=256
    # ideal_entropy = []
    # for i in range(length):
    #     prob1 = i/length
    #     prob0 = 1 - prob1
    #     h = 0.03* -1 * ((prob1 * np.log2(prob1)) + (prob0 * np.log2(prob0)))
    #     ideal_entropy.append(h)

    # #plt.figure()
    # axs.plot(x_bin, ideal_entropy, '--', label = 'Ideal entropy')

    plt.xticks(x_val, x_bin, rotation='vertical')
    #axs.grid()
    axs.yaxis.grid()
    axs.xaxis.grid()
    #axs.text(0.1, 0.5, f'avg={"{:.5f}".format(overall_avg_err)}, max={max_err}', horizontalalignment='left', verticalalignment='center', transform=axs.transAxes)
    if args.bit == True: 
        axs.set_title("Error in number of bits")
        plt.setp(axs, ylabel='avg error bits')
    else:
        axs.set_title("L1 Error Profile")
        plt.setp(axs, ylabel='avg L1 error')
    axs.legend(loc="upper right")
    plt.setp(axs, xlabel='Binary value x[7:0]')
    
    plt.figtext(0, 0, f"", ha="left", fontsize=7)

    #plt.savefig(f'result/Jeavons/entropy.png')
    save_name = 'result/Jeavons/gaines_majority_comparator_8bit_TRNG_lfsr.png'
    plt.savefig(f'{save_name}')
    print(f"Fig saved at {save_name}")

if __name__ == "__main__":
    main()