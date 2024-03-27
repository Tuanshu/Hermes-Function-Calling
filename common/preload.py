
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)
import torch


## preloading model here
model_path='NousResearch/Hermes-2-Pro-Mistral-7B'

preloaded_model=AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            return_dict=True,
            quantization_config=None, # none for not quantization
            torch_dtype=torch.float16,
            # attn_implementation="flash_attention_2",
            device_map="auto",
        )
preloaded_tokenizer=AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
