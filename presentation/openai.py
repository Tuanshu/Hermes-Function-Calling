import base64
import copy
import json
import re
import time
from argparse import ArgumentParser
from contextlib import asynccontextmanager
from typing import Dict, List, Literal, Optional, Tuple, Union

from fastapi import APIRouter, FastAPI, HTTPException,Depends
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk, ChatCompletionMessageParam, completion_create_params
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from typing import List,Dict,AsyncGenerator

from utils_logger import logger
from application.functioncall_use_case import FunctionCallUseCase
from application.stanalone_use_case import StandaloneUseCase

from common.dependencies import get_standalone_use_case
from .dto import SSEDataError,SSEDataIMain,SSEDataInit,SSEDataToolCall,SSEType,SSEDataDone,ChatCompletionResponse, ChatCompletionRequest,ChatMessage,ChatCompletionResponseChoice
# temp
# from transformers import AutoModelForCausalLM, AutoTokenizer


router = APIRouter()

# standalone API, not streaming
@router.post('/completions', response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest, standalone_use_case:StandaloneUseCase=Depends(get_standalone_use_case)):
    # logger.info(f'openai-like api called, first messages={request.messages[0].model_dump_json()}')
    if request.stream:  # 假设stream是请求模型的一部分
        raise NotImplementedError('streaming not yet implmented.')
        
    else:
        response_string =await standalone_use_case.run_inference_string(prompt=request.messages)
        choice_data = ChatCompletionResponseChoice(
        index=0,
        message=ChatMessage(role='assistant',content=response_string),
        finish_reason='stop',
        )
        response_model=ChatCompletionResponse(model=request.model, choices=[choice_data], object='chat.completion' ,messages=[],failures=[])  
        print(f'response_model={response_model.model_dump_json()}')                                     
        return response_model


@router.post('/completions-raw', response_model=ChatCompletionResponse)
async def create_chat_completion_raw(request: ChatCompletionRequest, standalone_use_case:StandaloneUseCase=Depends(get_standalone_use_case)):
    # logger.info(f'openai-like api called, first messages={request.messages[0].model_dump_json()}')
    if request.stream:  # 假设stream是请求模型的一部分
        raise NotImplementedError('streaming not yet implmented.')
        
    else:
        response_string =await standalone_use_case.run_inference(prompt=request.messages)
        choice_data = ChatCompletionResponseChoice(
        index=0,
        message=ChatMessage(role='assistant',content=response_string),
        finish_reason='stop',
        )     
        response_model=ChatCompletionResponse(model=request.model, choices=[choice_data], object='chat.completion' ,messages=[],failures=[])                                                
        print(f'response_model={response_model.model_dump_json()}')
        return response_model


