# Simulator Implementation

Work is located at:

[GitHub - pan185/SCSim](https://github.com/pan185/SCSim)

# Bitstream Generation

## 1. Jeavons 1994: Majority module

[Device for Generating Binary Sequences for Stochastic Computing](https://www.notion.so/Device-for-Generating-Binary-Sequences-for-Stochastic-Computing-907932ab99fc4863ab1096504e8e20df) 

## 2. Gaines 1969: Summation of binary weighted independent bitstreams

[Stochastic computing systems](https://www.notion.so/Stochastic-computing-systems-be8fb2b4636540cba62b46747349cbf1) 

## 3. LFSR+comparator

Using arbitrary seed and fpoly

## 4. LD sequence: Sobol

TODO

## 5. LD sequence: Halton

TODO

## Takeaways

![gaines_majority_comparator_8bit_TRNG_lfsr.png](Simulator%20Implementation%20e57ea7aeebda40a7bcf9e71939424b36/gaines_majority_comparator_8bit_TRNG_lfsr.png)

Takeaway1: Using LFSR+Comparator approach is very accurate since for full length bitstreams worst-case error is 1/256~=0.39%. But TRNG+Jeavons and Gaines approaches are explored to see if they are good solution to combat correlation problem.

# Compute Kernels