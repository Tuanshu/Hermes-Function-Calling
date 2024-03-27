from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .preload import preloaded_model, preloaded_tokenizer
from application.functioncall_use_case import FunctionCallUseCase

# db session for test prupose
def get_function_call_use_case() -> FunctionCallUseCase:
    return FunctionCallUseCase(preloaded_model, preloaded_tokenizer)

