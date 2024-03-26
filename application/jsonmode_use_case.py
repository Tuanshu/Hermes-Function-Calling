import argparse
import torch
import json

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)

from validator import validate_json_data

from utils import (
    print_nous_text_art,
    inference_logger,
    get_assistant_message,
    get_chat_template,
    validate_and_extract_tool_calls
)
from utils_logger import logger

# create your pydantic model for json object here
from typing import List, Optional,Dict,Union
from pydantic import BaseModel

class Character(BaseModel):
    name: str
    species: str
    role: str
    personality_traits: Optional[List[str]]
    special_attacks: Optional[List[str]]

    class Config:
        schema_extra = {
            "additionalProperties": False
        }

# serialize pydantic model into json schema
pydantic_schema = Character.schema_json()

class ModelInference:
    def __init__(self, model,tokenizer):
        self.chat_template="chatml"
        
        inference_logger.info(print_nous_text_art())

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

    def generate_json_completion(self, query, max_depth=5):

        try:
            depth = 0
            # sys_prompt = "You are a helpful assistant that answers in JSON. Here's the json schema you must adhere to:\n<schema>\n{schema}\n<schema>"
            sys_prompt = f"You are a helpful assistant that answers in JSON. Here's the json schema you must adhere to:\n<schema>\n{pydantic_schema}\n<schema>"

            prompt:List[Dict[str,str]] = [{"role": "system", "content": sys_prompt}]
            prompt.append({"role": "user", "content": query})

            inference_logger.info(f"Running inference to generate json object for pydantic schema:\n{json.dumps(json.loads(pydantic_schema), indent=2)}")
            completion = self.run_inference(prompt)

            def recursive_loop(prompt:List[Dict[str,str]], completion:str, depth:int):
                output:str=""

                nonlocal max_depth

                assistant_message = get_assistant_message(completion, self.chat_template, self.tokenizer.eos_token)

                tool_message = f"Agent iteration {depth} to assist with user query: {query}\n"
                if assistant_message is not None:
                    validation, json_object, error_message = validate_json_data(assistant_message, json.loads(pydantic_schema))
                    if validation:
                        inference_logger.info(f"Assistant Message:\n{assistant_message}")
                        output+=assistant_message
                        inference_logger.info(f"json schema validation passed")
                        inference_logger.info(f"parsed json object:\n{json.dumps(json_object, indent=2)}")
                        return output
                    elif error_message:
                        inference_logger.info(f"Assistant Message:\n{assistant_message}")
                        output+=assistant_message

                        inference_logger.info(f"json schema validation failed")
                        tool_message += f"<tool_response>\nJson schema validation failed\nHere's the error stacktrace: {error_message}\nPlease return corrrect json object\n<tool_response>"
                        
                        depth += 1
                        if depth >= max_depth:
                            print(f"Maximum recursion depth reached ({max_depth}). Stopping recursion.")
                            return output
                        
                        prompt.append({"role": "tool", "content": tool_message})
                        completion = self.run_inference(prompt)
                        output+=recursive_loop(prompt, completion, depth)
                else:
                    inference_logger.warning("Assistant message is None")
                    return output
            return recursive_loop(prompt, completion, depth)
        except Exception as e:
            inference_logger.error(f"Exception occurred: {e}")
            raise e

