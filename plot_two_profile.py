#!/usr/bin/python
import Jeavons_1994_scaling
import util
import os
import sys
import matplotlib.pyplot as plt
import argparse
import numpy as np

file1_n = "result/Jeavons/majority_8_M_1024_cycle_avg_err.txt"
file3_n = "result/Jeavons/majority_8_M_2048_cycle_avg_err.txt"
file2_n = "result/Jeavons/majority_8_M_10240_cycle_avg_err.txt"

file1 = open(file1_n, 'r')
Lines = file1.readlines()
err_1024 = []
err_one_third=[]
two = 1.414
two_arr=[]
# Strips the newline character
for line in Lines:
    err_1024.append(float(line.strip()))
    err_one_third.append(float(line.strip())/3.16227766017)
    two_arr.append(float(line.strip())/two)

file2 = open(file2_n, 'r')
Lines2 = file2.readlines()
err_10240 = []
# Strips the newline character
for line2 in Lines2:
    err_10240.append(float(line2.strip()))

file3 = open(file3_n, 'r')
Lines3 = file3.readlines()
err_2048 = []
# Strips the newline character
for line3 in Lines3:
    err_2048.append(float(line3.strip()))

fig, axs = plt.subplots(1)
fig.set_size_inches(45, 12)
axs.set_prop_cycle(color=['#9cc0e7', '#3caea3', '#f6d55c', '#9ec4c5', '#faeacb'])#'#ed553b'])
fig.suptitle(f'TRNG bitstream len = [1024, 10240], across 100 iterations, using majority scheme')
plt.subplots_adjust(hspace = 0.4)
x_val = np.linspace(0, 2**8 - 1, 2**8)
x_bin = []
for index in range(len(x_val)): 
    bin_string = bin(int(x_val[index]))
    bin_string = bin_string[2:]
    if len(bin_string) < 8:
        bin_string = bin_string.zfill(8)
    x_bin.append(bin_string)
axs.plot(x_bin, err_1024, 'o-', markersize=5, label='length=1024')
axs.plot(x_bin, err_10240, 'o-', markersize=5, label='length=10240')
axs.plot(x_bin, err_2048, 'o-', markersize=5, label='length=2048')
axs.plot(x_bin, err_one_third, '--', markersize=5, label='1/sq(10)*blue curve')
axs.plot(x_bin, two_arr, '--', markersize=5, label='1/sq(2)*blue curve')
plt.xticks(x_val, x_bin, rotation='vertical')
axs.grid()
#axs.text(0.1, 0.5, f'avg={"{:.5f}".format(overall_avg_err)}, max={max_err}', horizontalalignment='left', verticalalignment='center', transform=axs.transAxes)
axs.set_title("L1 Error Profile")
axs.legend(loc="upper right")
plt.setp(axs, xlabel='Binary value x[3:0]')
plt.setp(axs, ylabel='avg L1 error')
plt.figtext(0, 0, f"", ha="left", fontsize=7)
plt.savefig(f'result/Jeavons/majority_8_M_1024_10240.png')