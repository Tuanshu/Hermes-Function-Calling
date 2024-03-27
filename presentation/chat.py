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

from common.dependencies import get_function_call_use_case,get_standalone_use_case
from common.preload import preloaded_model,preloaded_tokenizer
from .dto import SSEDataError,SSEDataIMain,SSEDataInit,SSEDataToolCall,SSEType,SSEDataDone,ChatCompletionResponse, ChatCompletionRequest,ChatMessage,ChatCompletionResponseChoice
# temp
# from transformers import AutoModelForCausalLM, AutoTokenizer


router = APIRouter()


@router.post('/v1/chat/completions', response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest, function_use_case=Depends(get_function_call_use_case)):
    logger.info(f'openai-like api called, first messages={request.messages[0].model_dump_json()}')
    if request.stream:  # 假设stream是请求模型的一部分
        return await chat_completion_stream(request, function_use_case)
        
    else:
        return await chat_completion_not_stream(request, function_use_case)



async def chat_completion_not_stream(request: ChatCompletionRequest, function_use_case:FunctionCallUseCase):

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

    # not respecting function for now

    # input_message = request.messages[-1]
    # query=input_message.content
    # generator:AsyncGenerator[ChatMessage, None]=function_use_case.achat(query=query)
    generator:AsyncGenerator[ChatMessage, None]=function_use_case.achat(previous_messages=request.messages)

    return StreamingResponse(
        main_stream(generator),
        media_type="text/event-stream",
        headers={"content-type": "text/event-stream"},
    )  # HACK: force response header to align chatgpt-ui (from text/event-stream; charset=utf-8)


# 對應test code中的main
async def main_stream(generator: AsyncGenerator[ChatMessage, None]):
    first_flag = True
    tool_called = False
    event_id = 1
    try:
        async for message in generator:
            if first_flag:
                current_sse_data = SSEDataInit()
                yield f'id: {event_id}\nevent: {SSEType.INIT.value}\ndata: {current_sse_data.model_dump_json()}\n\n'
                event_id += 1
                first_flag = False

            # 可能需要tool_called flag, 是因為最後儲存時還會再呼叫一次, 可能會導致重複出現
            # if message.get('role') == 'tool_call_args' and not tool_called:
            if message.role == 'tool_call_args' and not tool_called:

                current_sse_data = SSEDataToolCall()
                yield f"id: {event_id}\nevent: tool_call\ndata: {current_sse_data.model_dump_json()}\n\n"
                event_id += 1
                tool_called = True
                continue

            # HACK: 為了避免tool_call之後還有message, 故僅在not tool call時回傳message event
            # (但message還是會更新, 以獲取total_token, 只是不傳給用戶)
            if not tool_called:
                # current_sse_data = SSEDataIMain(choices=[ChatCompletionResponseChoice(message=ChatMessage(role=message.get('role'),content=message.get('content')))])
                current_sse_data = SSEDataIMain(choices=[ChatCompletionResponseChoice(message=ChatMessage(role=message.role,content=message.content))])
                yield f"id: {event_id}\nevent: {SSEType.BODY.value}\ndata: {current_sse_data.model_dump_json()}\n\n"
                event_id += 1

    except Exception as exc:
        error_message = str(exc)
        logger.error(f"An error occurred during streaming: {error_message}")
        current_sse_data=SSEDataError(detail=error_message)
        yield f'id: {event_id}\nevent: {SSEType.ERROR.value}\ndata: {current_sse_data.model_dump_json()}\n\n'
        return  # exception發生後, 不回傳done, 也不raise error到外側 (因為已經開始streaming)

    # Done, last message handling

    current_sse_data=SSEDataDone()
    yield f'id: {event_id}\nevent: {SSEType.DONE.value}\ndata: {current_sse_data.model_dump_json()}\n\n'
