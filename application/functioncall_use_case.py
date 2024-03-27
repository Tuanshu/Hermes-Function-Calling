import argparse
import torch
import json

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)
from requests.exceptions import HTTPError

from application import avaliable_functions
from prompter import PromptManager
from validator import validate_function_call_schema
import requests
from typing import List,Dict,AsyncGenerator

from utils import (
    print_nous_text_art,
    inference_logger,
    get_assistant_message,
    get_chat_template,
    validate_and_extract_tool_calls
)

from domain_models import ChatMessage

# HACK: !!!!!!!
from presentation.dto import ChatCompletionResponse,ChatCompletionRequest


# TS set seed
seed_value = 41
torch.manual_seed(seed_value)



class FunctionCallUseCase:
    def __init__(self, model,tokenizer):
        self.chat_template="chatml"

        inference_logger.info(print_nous_text_art())
        self.prompter = PromptManager()
        self.bnb_config = None

        self.model = model

        self.tokenizer = tokenizer
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"

        if self.tokenizer.chat_template is None:
            print("No chat template defined, getting chat_template...")
            self.tokenizer.chat_template = get_chat_template(self.chat_template)
        
        inference_logger.info(self.model.config)
        inference_logger.info(self.model.generation_config)
        inference_logger.info(self.tokenizer.special_tokens_map)

    def process_completion_and_validate(self, completion, chat_template):

        assistant_message = get_assistant_message(completion, chat_template, self.tokenizer.eos_token)

        if assistant_message:
            validation, tool_calls, error_message = validate_and_extract_tool_calls(assistant_message)

            if validation:
                inference_logger.info(f"parsed tool calls:\n{json.dumps(tool_calls, indent=2)}")
                return tool_calls, assistant_message, error_message
            else:
                tool_calls = None
                return tool_calls, assistant_message, error_message
        else:
            inference_logger.warning("Assistant message is None")
            raise ValueError("Assistant message is None")
        
    def execute_function_call(self, tool_call:Dict):
        function_name = tool_call.get("name")
        function_to_call = getattr(avaliable_functions, function_name, None)
        function_args = tool_call.get("arguments", {})

        inference_logger.info(f"[ts] function_args: {function_args}")
        inference_logger.info(f"[ts] function_to_call: {function_to_call}")

        inference_logger.info(f"Invoking function call {function_name} ...")
        function_response = function_to_call(*function_args.values())
        results_dict = f'{{"name": "{function_name}", "content": {function_response}}}'
        return results_dict
    
    def run_inference(self, prompt):

        # apply_chat_template是transormers預設的方法, 居然好像可以直接處理pydantic model, 而且似乎空的function_call沒造成影響
        # 好像是因為裡面有ctx = self.new_context(dict(*args, **kwargs))

        inputs = self.tokenizer.apply_chat_template(
            prompt,
            add_generation_prompt=True,
            return_tensors='pt'
        )

        tokens = self.model.generate(
            inputs.to(self.model.device),
            max_new_tokens=1500,
            temperature=0.8,
            repetition_penalty=1.1,
            do_sample=True,
            eos_token_id=self.tokenizer.eos_token_id,
        )
        completion = self.tokenizer.decode(tokens[0], skip_special_tokens=False, clean_up_tokenization_space=True)
        return completion

    def call_inference(self, prompt) -> str:
        request=ChatCompletionRequest(messages=prompt)
        try:
            response = requests.post(f"http://210.58.113.45:6616/openai/completions-raw",json=request.model_dump())  # /ces/boards/
            response.raise_for_status()
            pydantic_response:ChatCompletionResponse = ChatCompletionResponse.model_validate(response.json())
            return  pydantic_response.choices[-1].message.content
        except HTTPError as http_err:
            if response.status_code == 422:
                # Handle 422 error specifically
                error_details = response.json()  # Assuming the error details are in JSON format
                raise ValueError(f"Error 422: Unprocessable Entity. Details: {error_details}")
            else:
                # Handle other HTTP errors
                raise ValueError(f"HTTP error occurred: {http_err}")

    # def run_inference_from_messages(self, messages:List[ChatMessage]):
    #     prompt:List[Dict]= [message.model_dump().pop('function_call') for message in messages]

    #     inputs = self.tokenizer.apply_chat_template(
    #         prompt,
    #         add_generation_prompt=True,
    #         return_tensors='pt'
    #     )

    #     tokens = self.model.generate(
    #         inputs.to(self.model.device),
    #         max_new_tokens=1500,
    #         temperature=0.8,
    #         repetition_penalty=1.1,
    #         do_sample=True,
    #         eos_token_id=self.tokenizer.eos_token_id,
    #     )
    #     completion = self.tokenizer.decode(tokens[0], skip_special_tokens=False, clean_up_tokenization_space=True)
    #     return completion

    # this is a async generator (with yield instead of return)
    #async def achat(self, query, num_fewshot=None, max_depth=5)->AsyncGenerator[ChatMessage, None]:

    async def achat(self, previous_messages:List[ChatMessage], num_fewshot=None, max_depth=5)->AsyncGenerator[ChatMessage, None]:

        try:
            depth = 0

            if isinstance(previous_messages,str): 
                user_message_content = f"{previous_messages}\nThis is the first turn and you don't have <tool_results> to analyze yet"
                previous_messages = [ChatMessage(role='user', content=user_message_content)]
            elif isinstance(previous_messages,list):
                 # fix last message (user)
                 last_message:ChatMessage = previous_messages[-1]
                 assert last_message.role == 'user', 'the latest message is not from user!'

                 query = last_message.content
                 last_message.content=f"{query}\nThis is the first turn and you don't have <tool_results> to analyze yet"

            #tools = avaliable_functions.get_openai_tool_dicts()
            # 因為@tool (from langchain看起來會限制只有一個input, 可能用arg_schema可解), 所以改在生成openai_tool_desc處加上tool()
            tools = avaliable_functions.get_openai_tool_dicts_no_at_tool_dec()

            messages:List[ChatMessage] = self.prompter.generate_prompt_from_messages(previous_messages, tools, num_fewshot)
            user_message=messages[-1]
            yield user_message # the last message in generate_prompt is usr message. system message omitted.

            async def arecursive_loop(messages:List[ChatMessage], depth)->AsyncGenerator[ChatMessage, None]:
                nonlocal max_depth # 好像不太需要nonlocal? 不太確定

                # move run_inference here
                print(f'[ts] check messages type before run_inference={type(messages[-1])}')


                #completion = self.run_inference(messages)
                completion = self.call_inference(messages)


                tool_calls, assistant_message_content, error_message = self.process_completion_and_validate(completion, self.chat_template)
                tool_calls:List[Dict]

                # assistant_message={"role": "assistant", "content": assistant_message_content}
                assistant_message=ChatMessage(role="assistant",content=assistant_message_content)
                messages.append(assistant_message)
                yield assistant_message # addtional yield
                inference_logger.info(f"Assistant Message:\n{assistant_message_content}")

                tool_message = f"Agent iteration {depth} to assist with user query: {query}\n" # Don't need this line?
                
                # check 是否達到max_depth
                depth += 1
                if depth >= max_depth:
                    print(f"Maximum recursion depth reached ({max_depth}). Stopping recursion.")
                    return # 結束generator

                if tool_calls:

                    for tool_call in tool_calls:
                        validation, message = validate_function_call_schema(tool_call, tools)
                        if validation:
                            try:
                                function_response = self.execute_function_call(tool_call)
                                tool_message += f"<tool_response>\n{function_response}\n</tool_response>\n"
                                inference_logger.info(f"Here's the response from the function call: {tool_call.get('name')}\n{function_response}")
                            except Exception as e:
                                inference_logger.info(f"Could not execute function: {e}")
                                tool_message += f"<tool_response>\nThere was an error when executing the function: {tool_call.get('name')}\nHere's the error traceback: {e}\nPlease call this function again with correct arguments within XML tags <tool_call></tool_call>\n</tool_response>\n"
                        else:
                            inference_logger.info(message)
                            tool_message += f"<tool_response>\nThere was an error validating function call against function signature: {tool_call.get('name')}\nHere's the error traceback: {message}\nPlease call this function again with correct arguments within XML tags <tool_call></tool_call>\n</tool_response>\n"

                    #tool_response_message={"role": "tool", "content": tool_message}
                    tool_response_message=ChatMessage(role="tool",content=tool_message)


                    messages.append(tool_response_message)
                    yield tool_response_message # addtional yield

                    # completion = self.run_inference(messages)

                    # yield arecursive_loop(messages, completion, depth)
                    async for deeper_value in arecursive_loop(messages, depth):
                        yield deeper_value


                elif error_message:
                    tool_message += f"<tool_response>\nThere was an error parsing function calls\n Here's the error stack trace: {error_message}\nPlease call the function again with correct syntax<tool_response>"

                    #new_message={"role": "tool", "content": tool_message}
                    tool_error_message=ChatMessage(role="tool",content=tool_message)
                    
                    messages.append(tool_error_message)
                    yield tool_error_message # addtional yield

                    # completion = self.run_inference(messages)
                    # yield arecursive_loop(messages, completion, depth)
                    async for deeper_value in arecursive_loop(messages, depth):
                        yield deeper_value


            # FIXME: 感覺一直出現以下pattern很醜, 但暫時不知道如何解決
            # yield arecursive_loop(messages, completion, depth)
            async for value in arecursive_loop(messages, depth):
                yield value


        except Exception as e:
            inference_logger.error(f"Exception occurred: {e}")
            raise e
        

    # this is a async generator (with yield instead of return)
    def chat(self, query, num_fewshot=None, max_depth=5)-> ChatMessage:
        try:
            depth = 0
            user_message_content = f"{query}\nThis is the first turn and you don't have <tool_results> to analyze yet"
            chat = [{"role": "user", "content": user_message_content}]
            #tools = avaliable_functions.get_openai_tool_dicts()
            # 因為@tool (from langchain看起來會限制只有一個input, 可能用arg_schema可解), 所以改在生成openai_tool_desc處加上tool()
            tools = avaliable_functions.get_openai_tool_dicts_no_at_tool_dec()

            messages:List[ChatMessage] = self.prompter.generate_prompt(chat, tools, num_fewshot)

            def recursive_loop(messages:List[ChatMessage], depth)->ChatMessage:
                nonlocal max_depth # 好像不太需要nonlocal? 不太確定

                # move run_inference here
                completion = self.run_inference(messages)
                tool_calls, assistant_message_content, error_message = self.process_completion_and_validate(completion, self.chat_template)
                tool_calls:List[Dict]

                assistant_message={"role": "assistant", "content": assistant_message_content}
                messages.append(assistant_message)
                inference_logger.info(f"Assistant Message:\n{assistant_message_content}")

                tool_message = f"Agent iteration {depth} to assist with user query: {query}\n" # Don't need this line?
                
                # check 是否達到max_depth
                depth += 1
                if depth >= max_depth:
                    print(f"Maximum recursion depth reached ({max_depth}). Stopping recursion.")
                    return messages # 結束

                # 假設沒tool_calls or error_message, 也return

                if (not tool_calls) and (not error_message):
                    print(f"No more tool call. Stopping recursion.")
                    return messages # 結束

                if tool_calls:

                    for tool_call in tool_calls:
                        validation, message = validate_function_call_schema(tool_call, tools)
                        if validation:
                            try:
                                function_response = self.execute_function_call(tool_call)
                                tool_message += f"<tool_response>\n{function_response}\n</tool_response>\n"
                                inference_logger.info(f"Here's the response from the function call: {tool_call.get('name')}\n{function_response}")
                            except Exception as e:
                                inference_logger.info(f"Could not execute function: {e}")
                                tool_message += f"<tool_response>\nThere was an error when executing the function: {tool_call.get('name')}\nHere's the error traceback: {e}\nPlease call this function again with correct arguments within XML tags <tool_call></tool_call>\n</tool_response>\n"
                        else:
                            inference_logger.info(message)
                            tool_message += f"<tool_response>\nThere was an error validating function call against function signature: {tool_call.get('name')}\nHere's the error traceback: {message}\nPlease call this function again with correct arguments within XML tags <tool_call></tool_call>\n</tool_response>\n"

                    tool_response_message={"role": "tool", "content": tool_message}
                    messages.append(tool_response_message)

                    # completion = self.run_inference(messages)

                    # yield arecursive_loop(messages, completion, depth)
                    return recursive_loop(messages, depth)


                elif error_message:
                    tool_message += f"<tool_response>\nThere was an error parsing function calls\n Here's the error stack trace: {error_message}\nPlease call the function again with correct syntax<tool_response>"

                    new_message={"role": "tool", "content": tool_message}
                    messages.append(new_message)

                    # completion = self.run_inference(messages)
                    # yield arecursive_loop(messages, completion, depth)
                    return recursive_loop(messages, depth)
                
                    

            # FIXME: 感覺一直出現以下pattern很醜, 但暫時不知道如何解決
            # yield arecursive_loop(messages, completion, depth)
            return recursive_loop(messages, depth)


        except Exception as e:
            inference_logger.error(f"Exception occurred: {e}")
            raise e