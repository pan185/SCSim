# %%
import torch

import sys
sys.path.append('/Users/zhewenpan/Repo/')
#print(sys.path)
from SCSim.Jeavons_1994 import SNG
from SCSim.util import global_vars
from SCSim.metric.metric import Correlation

# %%
corr = Correlation().cpu()

# %%
globalVar = global_vars(8, 256, 100)
sng_a = SNG(globalVar, 'comparator', 'lfsr')(128)
sng_b = SNG(globalVar, 'comparator', 'lfsr')(128)
# %%
print(len(sng_a))
print(len(sng_b))
# %%
for i in range(len(sng_a)):
    a = torch.tensor(sng_a[i]).type(torch.int8).cpu()
    b = torch.tensor(sng_b[i]).type(torch.int8).cpu()
    corr.Monitor(a,b)

# %%
print("d", corr.paired_00_d)
print("c", corr.paired_01_c)
print("b", corr.paired_10_b)
print("a", corr.paired_11_a)

cor = corr()
print("correlation", cor)