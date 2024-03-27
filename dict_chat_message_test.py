from domain_models import ChatMessage


test_item=ChatMessage(role='system',content='hello')


print(dict(test_item))
# {'role': 'system', 'content': 'hello', 'function_call': None}