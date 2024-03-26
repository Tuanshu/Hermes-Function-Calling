 poetry shell
 在shell裡工作

 try 
 
 pip install -U wheel
 pip install -U flash-attn --no-build-isolation 

 (hermes-function-calling-py3.10) [centos@fu-yuan Hermes-Function-Calling]$ nvcc -V
nvcc: NVIDIA (R) Cuda compiler driver
Copyright (c) 2005-2021 NVIDIA Corporation
Built on Thu_Nov_18_09:45:30_PST_2021
Cuda compilation tools, release 11.5, V11.5.119
Build cuda_11.5.r11.5/compiler.30672275_0

發現ncvv好像真的指錯cuda

 CUDA Version: 12.2

(hermes-function-calling-py3.10) [centos@fu-yuan local]$ ls -a
.  ..  bin  cuda  cuda-11.5

可能是指到了cuda-11.5

https://blog.csdn.net/qq_45934285/article/details/130552500


Multiple CUDA versions on machine nvcc -V confusion
https://stackoverflow.com/questions/40517083/multiple-cuda-versions-on-machine-nvcc-v-confusion

Different CUDA versions shown by nvcc and NVIDIA-smi
https://stackoverflow.com/questions/53422407/different-cuda-versions-shown-by-nvcc-and-nvidia-smi


因為發現可能真的是我的cuda版本(11.5)不夠 所以先不管 nvcc -v比較準
            # attn_implementation="flash_attention_2",


Error fetching current price for TSLA: SQLite driver not installed!

https://stackoverflow.com/questions/19530974/how-can-i-add-the-sqlite3-module-to-python/51031104#51031104

我可能需要 sqlite 總之先安裝 yum install sqlite-devel

pip install pysqlite3 


python functioncall.py --query "I need the current stock price of Tesla (TSLA)"

OK了

