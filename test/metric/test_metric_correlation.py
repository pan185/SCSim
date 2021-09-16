# %%
import torch
from SCSim.metric.metric import Correlation

# %%
corr = Correlation().cpu()

# %%
a = torch.tensor([0]).type(torch.int8).cpu()
b = torch.tensor([0]).type(torch.int8).cpu()
corr.Monitor(a,b)
# %%
a = torch.tensor([0]).type(torch.int8).cpu()
b = torch.tensor([1]).type(torch.int8).cpu()
corr.Monitor(a,b)
# %%
a = torch.tensor([1]).type(torch.int8).cpu()
b = torch.tensor([0]).type(torch.int8).cpu()
corr.Monitor(a,b)
# %%
a = torch.tensor([1]).type(torch.int8).cpu()
b = torch.tensor([1]).type(torch.int8).cpu()
# %%
corr.Monitor(a,b)
print("d", corr.paired_00_d)
print("c", corr.paired_01_c)
print("b", corr.paired_10_b)
print("a", corr.paired_11_a)

cor = corr()
print(cor)

# %%
a = torch.tensor([0]).type(torch.int8).cpu()

# %%
a = torch.tensor([1]).type(torch.int8).cpu()

# %%
corr.Monitor(a)
print("d", corr.paired_00_d)
print("c", corr.paired_01_c)
print("b", corr.paired_10_b)
print("a", corr.paired_11_a)

cor = corr()
print("correlation", cor)

# %%