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

from typing import List,Dict,AsyncGenerator,Union

from utils import (
    print_nous_text_art,
    inference_logger,
    get_assistant_message,
    get_chat_template,
    validate_and_extract_tool_calls
)

from domain_models import ChatMessage


# TS set seed
seed_value = 41
torch.manual_seed(seed_value)



class StandaloneUseCase:
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

    async def run_inference(self, prompt:List[Union[Dict[str,str],ChatMessage]]):

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

    async def run_inference_string(self, prompt:List[Union[Dict[str,str],ChatMessage]]):

        completion = await self.run_inference(prompt)

        return get_assistant_message(completion, self.chat_template, self.tokenizer.eos_token)
