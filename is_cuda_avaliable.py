import torch

# 检查 CUDA 是否可用
cuda_available = torch.cuda.is_available()

print("CUDA available:", cuda_available)
print("PyTorch version:", torch.__version__)

cuda_version = torch.version.cuda

print("CUDA version:", cuda_version)
# (hermes-function-calling-py3.10) [centos@fu-yuan Hermes-Function-Calling]$ python is_cuda_avaliable.py
# CUDA available: True
# PyTorch version: 2.1.2+cu121
# CUDA version: 12.1