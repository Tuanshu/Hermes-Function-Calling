from typing import Dict, List, Literal, Optional, Tuple, Union
from pydantic import BaseModel, Field
import time

from domain_models import ChatMessage


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    functions: Optional[List[Dict]] = None
    seed: Optional[int] = None  # ignoring, simply testing
    temperature: Optional[float] = 0
    top_p: Optional[float] = None  # ignoring, simply testing
    max_tokens: Optional[int] = None  # note, here the default is None not 10
    stream: Optional[bool] = False
    # https://platform.openai.com/docs/api-reference/completions/create
    # Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.
    stop: Optional[List[str]] = None


class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: Union[ChatMessage]
    finish_reason: Literal['stop', 'length', 'function_call']


class DeltaMessage(BaseModel):
    role: Optional[Literal['user', 'assistant', 'system']] = None
    content: Optional[str] = None


class ChatCompletionResponseStreamChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[Literal['stop', 'length']]


class ChatCompletionResponse(BaseModel):
    model: str
    object: Literal['chat.completion', 'chat.completion.chunk']
    choices: List[Union[ChatCompletionResponseChoice, ChatCompletionResponseStreamChoice]]
    messages:List[ChatMessage] # a temperary fields, returning all messages (may yield problem if there are some json problem)
    created: Optional[int] = Field(default_factory=lambda: int(time.time()))
    failures: List  # return some comment about the parsing

