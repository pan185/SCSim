#!/usr/bin/python
import Jeavons_1994_scaling
import util
import os
import sys
import matplotlib.pyplot as plt
import argparse
import numpy as np

PRECISION = 8

myfile1="result/Jeavons/scaling_analysis/avg_err_"
myfile2="result/Jeavons/scaling_analysis/max_err_"
dottxt = '.txt'
file_precision8 = '_precision8' + dottxt
file_precision4 = '_precision4' + dottxt

file1_majority = myfile1 + 'majority'
file2_majority = myfile2 + 'majority'
file1_pm = myfile1 + 'plus_multiply'
file2_pm = myfile2 + 'plus_multiply'
file1_pm_i = myfile1 + 'plus_multiply_inverse'
file2_pm_i = myfile2 + 'plus_multiply_inverse'

avg_file_arr = [file1_majority + dottxt, file1_pm + dottxt, file1_pm_i + dottxt]
max_file_arr = [file2_majority + dottxt, file2_pm + dottxt, file2_pm_i + dottxt]

precision8_files = [file1_majority + file_precision8, file1_pm + file_precision8, file1_pm_i + file_precision8]
precision4_files = [file1_majority + file_precision4, file1_pm + file_precision4, file1_pm_i + file_precision4]

name = ['majority', 'plus_multiply', 'plus_multiply_inverse']

def main(raw_args=None):
    #############
    # argparse
    #############
    parser = argparse.ArgumentParser()
    parser.add_argument('--plot', default=False, action='store_true', help='No computation, just plot using existing txt files')
    args = parser.parse_args(raw_args)

    if args.plot == False:
        if os.path.isfile(file1_majority) == False or os.path.isfile(file2_majority) == False: Jeavons_1994_scaling.main(['--scheme', 'majority'])
        if os.path.isfile(file1_pm) == False or os.path.isfile(file2_pm) == False: Jeavons_1994_scaling.main(['--scheme', 'plus_multiply'])
        if os.path.isfile(file1_pm_i) == False or os.path.isfile(file2_pm_i) == False: Jeavons_1994_scaling.main(['--scheme', 'plus_multiply_inverse'])
    
    #############
    # Visualization
    #############
    arr = [4, 5, 6, 7, 8, 9, 10]
    len_arr = []
    for len in arr: len_arr.append(2**len)

    fig, axs = plt.subplots(2)
    fig.set_size_inches(12, 8)
    fig.suptitle(f'Length scaling analysis: {len_arr} bit')
    plt.subplots_adjust(hspace = 0.4)
    axs[0].set_prop_cycle(color=['#3caea3', '#f6d55c', '#ed553b'])
    axs[1].set_prop_cycle(color=['#3caea3', '#f6d55c', '#ed553b'])

    #############
    # read files using readlines()
    #############
    for i in range(3):

        if args.plot == False: file1 = open(avg_file_arr[i], 'r')
        else: file1 = open(precision8_files[i], 'r')
        Lines = file1.readlines()
        avg = []
        # Strips the newline character
        for line in Lines:
            avg.append(float(line.strip()))

        if args.plot == False: file2 = open(max_file_arr[i], 'r')
        else: file2 = open(precision8_files[i], 'r')
        Lines2 = file2.readlines()
        max = []
        # Strips the newline character
        for line2 in Lines2:
            max.append(float(line2.strip()))

        #############
        # Overlap plots
        #############
        axs[0].plot(arr, avg, 'o-', markersize=5, label=name[i]+'_8bit')
        axs[1].plot(arr, max, 'o-', markersize=5, label=name[i]+'_8bit')
    
    if args.plot:
        for i in range(3):

            file1 = open(precision4_files[i], 'r') 
            Lines = file1.readlines()
            avg = []
            # Strips the newline character
            for line in Lines:
                avg.append(float(line.strip()))

            file2 = open(precision4_files[i], 'r') 
            Lines2 = file2.readlines()
            max = []
            # Strips the newline character
            for line2 in Lines2:
                max.append(float(line2.strip()))

            #############
            # Overlap plots
            #############
            axs[0].plot(arr, avg, '^--', markersize=5, label=name[i]+'_4bit')
            axs[1].plot(arr, max, '^--', markersize=5, label=name[i]+'_4bit')

    axs[0].grid()
    axs[0].set_title("Average error")
    axs[0].legend(loc="upper right")
    
    axs[1].grid()
    axs[1].set_title("Max error")
    axs[1].legend(loc="upper right")

    plt.setp(axs[0], ylabel='avg L1 error')
    plt.setp(axs[1], ylabel='max L1 error')
    plt.setp(axs[:], xlabel='TRNG bitstream length in bit = 2^x', xticks=arr)
    #plt.figtext(0, 0, f"", ha="left", fontsize=7)
    if args.plot: plot_name = 'result/Jeavons/scaling_analysis/length_4_8.png'
    else: plot_name = 'result/Jeavons/scaling_analysis/length_precision{PRECISION}.png'

    plt.savefig(plot_name)
    print(util.colorText.CGREEN + f'Done Jeavons length scaling analysis for all. See {plot_name}' + util.colorText.CEND)

if __name__ == "__main__":
    main()