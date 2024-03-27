看起來放置seed的位置會影響結果
放在最裡面
    def run_inference(self, prompt):
                # TS set seed
        seed_value = 41
        torch.manual_seed(seed_value)
是這樣
test.py
{'role': 'assistant', 'content': 'The current stock price of Tesla (TSLA) is $177.67. This information was retrieved directly from the function call result. If you have any further questions or need additional information, feel free to ask.'}
{'role': 'assistant', 'content': 'The current stock price of Tesla (TSLA) is $177.67. This information was retrieved directly from the function call result. If you have any further questions or need additional information, feel free to ask.'}


test_async_message.py with completion = self.run_inference(messages)
2024-03-27:09:32:23,250 INFO     [functioncall_use_case.py:194] Assistant Message:
The current stock price of Tesla (TSLA) is $177.67. This information was retrieved directly from the function call result. If you have any further questions or need additional information, feel free to ask.
The current stock price of Tesla (TSLA) is $177.67. This information was retrieved directly from the function call result. If you have any further questions or need additional information, feel free to ask.


test_async_message.py with completion = self.call_inference(messages) (這是在呼叫6616)
第一次是OK的
2024-03-27:09:34:36,925 INFO     [functioncall_use_case.py:194] Assistant Message:
The current stock price of Tesla (TSLA) is $177.67. This information was retrieved directly from the function call result. If you have any further questions or need additional information, feel free to ask.

2024-03-27:09:35:09,675 INFO     [functioncall_use_case.py:194] Assistant Message:
The current stock price of Tesla (TSLA) is $177.67. This information was retrieved directly from the function call result. If you have any further questions or need additional information, feel free to ask.

看起來沒問題 再來是把6615服務起起來
第一次OK
2024-03-27 09:36:34,334 - INFO - Assistant Message:
The current stock price of Tesla (TSLA) is $177.67. This information was retrieved directly from the function call result. If you have any further questions or need additional information, feel free to ask.

2024-03-27 09:37:00,986 - INFO - Assistant Message:
The current stock price of Tesla (TSLA) is $177.67. This information was retrieved directly from the function call result. If you have any further questions or need additional information, feel free to ask.

好像可以了, 所以seed要盡可能放在inference附近?
該不會是看太遠會變成有歷史之類的東西影響吧 因為是torch的seed, 且有preload的model

{
  "model": "",
  "messages": [
    {
      "role": "user",
      "content": "I need the current stock price of Tesla (TSLA)",
      "function_call": {}
    }
  ],
  "functions": [
    {}
  ],
  "seed": 42,
  "temperature": 0,
  "top_p": 0,
  "max_tokens": 0,
  "stream": true,
  "stop": [
    "string"
  ]
}

Standalone service

2024-03-27 09:54:11,961 - INFO - Assistant Message:
The current stock price of Tesla (TSLA) is $177.67. This information was retrieved directly from the function call result. If you have any further questions or need additional information, feel free to ask.

2024-03-27 09:54:46,077 - INFO - Assistant Message:
The current stock price of Tesla (TSLA) is $177.67. This information was retrieved directly from the function call result. If you have any further questions or need additional information, feel free to ask.