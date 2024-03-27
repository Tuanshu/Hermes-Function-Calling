import argparse
import torch
import json

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)

from application import avaliable_functions
from prompter import PromptManager
from validator import validate_function_call_schema

from typing import List,Dict

from utils import (
    print_nous_text_art,
    inference_logger,
    get_assistant_message,
    get_chat_template,
    validate_and_extract_tool_calls
)

from domain_models import ChatMessage

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
            eos_token_id=self.tokenizer.eos_token_id
        )
        completion = self.tokenizer.decode(tokens[0], skip_special_tokens=False, clean_up_tokenization_space=True)
        return completion

    def chat(self, query, num_fewshot=None, max_depth=5)->List[ChatMessage]:
        try:
            depth = 0
            user_message = f"{query}\nThis is the first turn and you don't have <tool_results> to analyze yet"
            chat = [{"role": "user", "content": user_message}]
            tools = avaliable_functions.get_openai_tool_dicts()
            messages:List[ChatMessage] = self.prompter.generate_prompt(chat, tools, num_fewshot)
            completion = self.run_inference(messages)

            def recursive_loop(messages:List[ChatMessage], completion, depth):
                nonlocal max_depth
                tool_calls, assistant_message, error_message = self.process_completion_and_validate(completion, self.chat_template)
                tool_calls:List[Dict]

                messages.append({"role": "assistant", "content": assistant_message})

                tool_message = f"Agent iteration {depth} to assist with user query: {query}\n"
                if tool_calls:
                    inference_logger.info(f"Assistant Message:\n{assistant_message}")

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
                    messages.append({"role": "tool", "content": tool_message})

                    depth += 1
                    if depth >= max_depth:
                        print(f"Maximum recursion depth reached ({max_depth}). Stopping recursion.")
                        return messages

                    completion = self.run_inference(messages)
                    return recursive_loop(messages, completion, depth)
                elif error_message:
                    inference_logger.info(f"Assistant Message:\n{assistant_message}")
                    tool_message += f"<tool_response>\nThere was an error parsing function calls\n Here's the error stack trace: {error_message}\nPlease call the function again with correct syntax<tool_response>"
                    messages.append({"role": "tool", "content": tool_message})

                    depth += 1
                    if depth >= max_depth:
                        print(f"Maximum recursion depth reached ({max_depth}). Stopping recursion.")
                        return messages

                    completion = self.run_inference(messages)
                    return recursive_loop(messages, completion, depth)
                else:
                    inference_logger.info(f"Assistant Message:\n{assistant_message}")
                    # the followiing is added by ts
                    messages.append({"role": "assistant", "content": assistant_message})
                    return messages
                
            return recursive_loop(messages, completion, depth)

        except Exception as e:
            inference_logger.error(f"Exception occurred: {e}")
            raise e



