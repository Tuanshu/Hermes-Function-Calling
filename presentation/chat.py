import base64
import copy
import json
import re
import time
from argparse import ArgumentParser
from contextlib import asynccontextmanager
from typing import Dict, List, Literal, Optional, Tuple, Union

from fastapi import APIRouter, FastAPI, HTTPException
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam, completion_create_params
from pydantic import BaseModel, Field

from utils_logger import logger
from presentation.dto import ChatCompletionResponse, ChatCompletionRequest,ChatMessage,ChatCompletionResponseChoice
from application.functioncall_use_case import FunctionCallUseCase
from preload import preloaded_model,preloaded_tokenizer
# temp
# from transformers import AutoModelForCausalLM, AutoTokenizer


router = APIRouter()



@router.post('/v1/chat/completions', response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest, function_use_case=FunctionCallUseCase(model=preloaded_model,tokenizer=preloaded_tokenizer)):
    logger.info(f'openai-like api called, first messages={request.messages[0].model_dump_json()}')
    if request.stream:  # 假设stream是请求模型的一部分
        return await chat_completion_stream(request, function_use_case)
    else:
        return await chat_completion_not_stream(request, function_use_case)



async def chat_completion_not_stream(request: ChatCompletionRequest, function_use_case:FunctionCallUseCase):
    logger.info(f'openai-like api called, first messages={request.messages[0].model_dump_json()}')

    # not respecting function for now

    input_message = request.messages[-1]
    query=input_message.content
    rtn_messages:List[ChatMessage]=function_use_case.chat(query=query)

    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=rtn_messages[-1],
        finish_reason='stop',
    )
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object='chat.completion' ,messages=rtn_messages,failures=[])



async def chat_completion_stream(request: ChatCompletionRequest, function_use_case:FunctionCallUseCase):
    logger.info(f'openai-like api called, fist messages={request.messages[0].model_dump_json()}')

    # not respecting function for now

    input_message = request.messages[-1]
    query=input_message.content
    rtn_messages:List[ChatMessage]=function_use_case.chat(query=query)

    choice_data = ChatCompletionResponseChoice(
        index=0,
        message=rtn_messages[-1],
        finish_reason='stop',
    )
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object='chat.completion' ,messages=rtn_messages,failures=[])