from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .preload import preloaded_model, preloaded_tokenizer
from application.functioncall_use_case import FunctionCallUseCase
from application.stanalone_use_case import StandaloneUseCase

# db session for test prupose
def get_function_call_use_case() -> FunctionCallUseCase:
    return FunctionCallUseCase(preloaded_model, preloaded_tokenizer)

def get_standalone_use_case() -> StandaloneUseCase:
    return StandaloneUseCase(preloaded_model, preloaded_tokenizer)
