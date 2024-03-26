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
# temp
# from transformers import AutoModelForCausalLM, AutoTokenizer


router = APIRouter()



@router.post('/v1/chat/completions', response_model=ChatCompletionResponse)
async def create_chat_completion(request: ChatCompletionRequest):
    logger.info(f'openai-like api called, fist messages={request.messages[0].json()}')
    gen_kwargs = {}
    # if request.top_k is not None:
    #     gen_kwargs['top_k'] = request.top_k
    if request.temperature is not None:
        if request.temperature < 0.01:
            gen_kwargs['top_k'] = 1  # greedy decoding
        else:
            # Not recommended. Please tune top_p instead.
            gen_kwargs['temperature'] = request.temperature
    if request.top_p is not None:
        gen_kwargs['top_p'] = request.top_p

    stop_words = add_extra_stop_words(request.stop)
    if request.functions:
        stop_words = stop_words or []
        if 'Observation:' not in stop_words:
            stop_words.append('Observation:')

    # TS: overwrite stop_words to request, since it will be handled in backend.
    request.stop = stop_words

    query, history, system = parse_messages(request.messages, request.functions)

    if query is _TEXT_COMPLETION_CMD:
        # response = text_complete_last_message(history, stop_words_ids=stop_words_ids, gen_kwargs=gen_kwargs, system=system)
        logger.info('the query is _TEXT_COMPLETION_CMD')
    else:
        logger.info('the query is not _TEXT_COMPLETION_CMD')

    # NOTE: 以下的block原本是else下的case, 是我移出來的
    ###########################################
    # response, _ = model.chat(
    #     tokenizer,
    #     query,
    #     history=history,
    #     system=system,
    #     stop_words_ids=stop_words_ids,
    #     **gen_kwargs,
    # )

    # recompose_messages的邏輯
    r_messages = recompose_messages(query, history, system)

    messages_as_dicts = [msg.dict() for msg in r_messages]

    # pop out null function_call

    for msg in messages_as_dicts:
        if msg['function_call'] == None:
            msg.pop('function_call')

    logger.info(f'messages_as_dicts={messages_as_dicts}')

    if request.model == '_gpt-3.5-turbo':
        request.model = 'gpt-3.5-turbo'
        response: ChatCompletion = openai_sync_client.chat.completions.create(
            seed=42,
            temperature=request.temperature,
            model=request.model,
            messages=messages_as_dicts,
            stream=False,
            max_tokens=request.max_tokens,
            stop=request.stop,
        )
    else:
        response: ChatCompletion = private_sync_client.chat.completions.create(
            seed=42,
            temperature=request.temperature,
            model=request.model,
            messages=messages_as_dicts,
            stream=False,
            max_tokens=request.max_tokens,
            stop=request.stop,
        )
    # message_dict = response.get("choices", [{}])[0].get("message", {})
    message_dict = dict(response.choices[0].message)

    # Create messages_response directly
    message_response = ChatMessage(**message_dict)
    response = message_response.content

    logger.info(f'llm raw response: {response}')
    # print('<chat>')
    # pprint(history, indent=2)
    # print(f'{query}\n<!-- *** -->\n{response}\n</chat>')
    #######################################################################
    # response = trim_stop_words(response, stop_words)
    if request.functions:
        choice_data, failures = parse_response(response, functions=request.functions)
    else:
        choice_data = ChatCompletionResponseChoice(
            index=0,
            message=ChatMessage(role='assistant', content=response),
            finish_reason='stop',
        )
        failures = []
    return ChatCompletionResponse(model=request.model, choices=[choice_data], object='chat.completion', failures=failures)

