#!/usr/bin/python
import Jeavons_1994
import util
import os
import sys
import matplotlib.pyplot as plt
import argparse
import numpy as np

myfile1="result/Jeavons/scaling_analysis/avg_err_"
myfile2="result/Jeavons/scaling_analysis/max_err_"
dottxt = '.txt'
ITER = 100

def cleanup(scheme):
    ## If file exists, delete it ##
    file1 = myfile1 + scheme + dottxt
    file2 = myfile2 + scheme + dottxt

    if os.path.isfile(file1):
        os.remove(file1)
    else:    ## Show an error ##
        print("Error: %s file not found" % file1)

    if os.path.isfile(file2):
        os.remove(file2)
    else:    ## Show an error ##
        print("Error: %s file not found" % file2)

def run_precision(prec_arr, scheme='majority'):
    #######################
    # Clean up txt file
    #######################
    cleanup(scheme)
    
    # for each precision
    for precision in prec_arr:
        prec_string = str(precision)
        Jeavons_1994.main(['--prec', prec_string, '--iter', str(ITER), '--scheme', scheme])

    #############
    # read files using readlines()
    #############
    file1_n = myfile1 + scheme + dottxt
    file2_n = myfile2 + scheme + dottxt

    file1 = open(file1_n, 'r')
    Lines = file1.readlines()
    avg = []
    # Strips the newline character
    for line in Lines:
        avg.append(float(line.strip()))
    #print(avg)

    file2 = open(file2_n, 'r')
    Lines2 = file2.readlines()
    max = []
    # Strips the newline character
    for line2 in Lines2:
        max.append(float(line2.strip()))
    #print(max)

    #############
    # Visualization
    #############
    fig, axs = plt.subplots(2)
    fig.set_size_inches(12, 8)
    fig.suptitle(f'Precision scaling analysis: {prec_arr} bit')
    plt.subplots_adjust(hspace = 0.4)

    axs[0].plot(prec_arr, avg, 'o-', markersize=5)
    axs[0].grid()
    axs[0].set_title("Average error")

    axs[1].plot(prec_arr, max, 'o-', markersize=5)
    axs[1].grid()
    axs[1].set_title("Max error")

    plt.setp(axs[:], xlabel='Precision bit')
    plt.setp(axs[0], ylabel='avg L1 error')
    plt.setp(axs[1], ylabel='max L1 error')
    plt.figtext(0, 0, f"Run across {ITER} iterations, using {scheme} module", ha="left", fontsize=7)
    plt.savefig(f'result/Jeavons/scaling_analysis/precision_{scheme}.png')

    print(util.colorText.CGREEN + 'Done Jeavons precision scaling analysis' + util.colorText.CEND)
    
def run_length(len_exp_arr, scheme='majority'):
    #######################
    # Clean up txt file
    #######################
    cleanup(scheme)
    
    #len_exp_arr = [4,5,6,7,8,9,10] # from 16 to 1024
    len_arr = []
    for len in len_exp_arr: len_arr.append(2**len)

    # for each length
    for length in len_arr:
        len_string = str(length)
        Jeavons_1994.main(['--len',len_string, '--iter', str(ITER),'--scheme', scheme])

    #############
    # read files using readlines()
    #############
    file1_n = myfile1 + scheme + dottxt
    file2_n = myfile2 + scheme + dottxt

    file1 = open(file1_n, 'r')
    Lines = file1.readlines()
    avg = []
    # Strips the newline character
    for line in Lines:
        avg.append(float(line.strip()))
    #print(avg)

    file2 = open(file2_n, 'r')
    Lines2 = file2.readlines()
    max = []
    # Strips the newline character
    for line2 in Lines2:
        max.append(float(line2.strip()))
    #print(max)

    #############
    # Visualization
    #############
    fig, axs = plt.subplots(2)
    fig.set_size_inches(12, 8)
    fig.suptitle(f'TRNG bitstream length scaling analysis: {len_arr} bit')
    plt.subplots_adjust(hspace = 0.4)
    #plt.xticks(len_arr, len_arr)

    axs[0].plot(len_arr, avg, 'o-', markersize=5)
    axs[0].grid()
    axs[0].set_title("Average error")

    axs[1].plot(len_arr, max, 'o-', markersize=5)
    axs[1].grid()
    axs[1].set_title("Max error")

    plt.setp(axs[:], xlabel='TRNG bitstream length in bit', xticks=len_arr)
    plt.setp(axs[0], ylabel='avg L1 error')
    plt.setp(axs[1], ylabel='max L1 error')
    plt.figtext(0, 0, f"Run across {ITER} iterations using {scheme} module", ha="left", fontsize=7)
    plt.savefig(f'result/Jeavons/scaling_analysis/length_{scheme}.png')

    print(util.colorText.CGREEN + 'Done Jeavons length scaling analysis' + util.colorText.CEND)
    
def main(raw_args=None):
    #############
    # argparse
    #############
    parser = argparse.ArgumentParser()
    parser.add_argument('--scheme', type=str, default='majority', action='store', choices=['majority', 'other', 'two_min_term', 'plus_multiply', 'plus_multiply_inverse'], help='Set scheme name')
    parser.add_argument('--item', type=str, default='length', action='store', choices=['length', 'precision'], help='Set analysis type')
    parser.add_argument('--start', type=int, default=None, action='store', help='Set array starting point. For length analysis, array is exponent of 2.')
    parser.add_argument('--end', type=int, default=None, action='store', help='Set array ending point. For length analysis, array is exponent of 2.')
    args = parser.parse_args(raw_args)

    #######################
    # Run experiment suite
    #######################
    
    if args.item == 'length':
        if args.start == None and args.end == None: arr = [4,5,6,7,8,9,10] # Default
        elif args.start != None and args.end != None: 
            if args.end < args.start: raise Exception('Error: end should not be less than start!')
            arr = np.linspace(args.start, args.end, args.end - args.start + 1)
        else:
            sys.exit(f'Error: start and end must be set at the same time!')

        run_length(arr, args.scheme)

    elif args.item == 'precision':
        if args.start == None and args.end == None: arr = [4,5,6,7,8] # Default
        elif args.start != None and args.end != None: 
            if args.end < args.start: raise Exception('Error: end should not be less than start!')
            arr = np.linspace(args.start, args.end, args.end - args.start + 1)
        else:
            sys.exit(f'Error: start and end must be set at the same time!')

        run_precision(arr, args.scheme)
    
    

if __name__ == "__main__":
    main()