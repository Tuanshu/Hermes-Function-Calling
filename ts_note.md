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

python jsonmode.py --query "Please return a json object to represent Goku from the anime Dragon Ball Z?"
python application/functioncall_use_case.py --query "Please return a json object to represent Goku from the anime Dragon Ball Z?"
python test.py --query "what is 369x397?"


感覺問題就是langchain的@tool會overwrite function為BaseTool
    # by TS, not allowing overwrite
    # def __call__(self, tool_input: str, callbacks: Callbacks = None) -> str:
    #     """Make tool callable."""
    #     return self.run(tool_input, callbacks=callbacks)

python test.py --query "I need the current stock price of Tesla (TSLA)"


有@tool
{\'type\': \'function\', \'function\': {\'name\': \'code_interpreter\', \'description\': \'code_interpreter(code_markdown: str) -> dict | str - Execute the provided Python code string on the terminal using exec.\\n    The string should contain valid, executable and pure python code in markdown syntax.\\n    Code should also import any required python packages.\\n\\n    Parameters:\\n    - code_markdown (str): The Python code with markdown syntax to be executed.\\n      for eg. ```python\\n<code-string>\\n```\\n\\n    Returns:\\n    dict: A dictionary containing variables declared and values returned by function calls.\\n\\n    Note: Use this function with caution, as executing arbitrary code can pose security risks.\', \'parameters\': {\'type\': \'object\', \'properties\': {\'code_markdown\': {\'type\': \'string\'}}, \'required\': [\'code_markdown\']}}}, 


沒有@tool
{\'type\': \'function\', \'function\': {\'name\': \'code_interpreter\', \'description\': \'    Execute the provided Python code string on the terminal using exec.\\n    The string should contain valid, executable and pure python code in markdown syntax.\\n    Code should also import any required python packages.     Parameters:\\n    - code_markdown (str): The Python code with markdown syntax to be executed.\\n      for eg. ```python\\n<code-string>\\n```     Returns:\\n    dict: A dictionary containing variables declared and values returned by function calls.     Note: Use this function with caution, as executing arbitrary code can pose security risks.\\n    \', \'parameters\': {\'type\': \'object\', \'properties\': {\'code_markdown\': {\'type\': \'string\'}}, \'required\': [\'code_markdown\']}}}, 

1. 是否有@tool在產生文檔上的不同:
 a. 如果有, 則會多一個\'code_interpreter(code_markdown: str) -> dict | str的python style type hint.
 b. 如果沒有, 除了Parameters看起來OK外, Args和Notes和Returns在產生文檔時可能缺漏


 python test_async.py --query "I need the current stock price of Tesla (TSLA)"
 python test.py --query "I need the current stock price of Tesla (TSLA)"

 python test_async_message.py --query "I need the current stock price of Tesla (TSLA)"
