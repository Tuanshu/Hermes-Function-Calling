from typing import Dict, List, Literal, Optional, Tuple, Union
from pydantic import BaseModel, Field
import time
from enum import Enum as PyEnum
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
    index: int = 0
    message: Union[ChatMessage] # NOTE: 其實應該要用delata, 待會再處理
    finish_reason: Union[Literal['stop', 'length', 'function_call'],None] =None


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


class SSEType(PyEnum):
    INIT = 'userMessageId'
    BODY = 'message'
    TOOL_CALL = 'tool_call'
    ERROR = 'error'
    DONE = 'done'

DUMMY_USER_MSG_ID=0
DUMMY_CONVERSATION_ID="dummy_conversation_id"
DUMMY_SESSION_ID=""


class SSEDataInit(BaseModel): # according to openai 
    userMessageId:int =DUMMY_USER_MSG_ID
    conversation_id: str = DUMMY_CONVERSATION_ID

class SSEDataIMain(BaseModel): # according to openai 
    id:str =DUMMY_SESSION_ID
    object: str = "chat.completion.chunk"
    created: int = 1711500000 # unix time
    model: str = "gpt-35-turbo-16k"
    system_fingerprint:str = None # not sure
    choices: List[ChatCompletionResponseChoice]


class SSEDataToolCall(BaseModel): # this is for generating args to UI, openai do not have tihs behavior
    content:List[str] = ['dummy_arg_1','dummy_arg_2']


class SSEDataError(BaseModel): # according to openai 
    detail:str =""

DUMMY_BOT_MSG_ID=1
DUMMY_CONVERSATION_ID="dummy_conversation_id"

class SSEDataDone(BaseModel): # according to openai 
    messageId:int =DUMMY_BOT_MSG_ID
    conversationId: str = DUMMY_CONVERSATION_ID
    total_tokens: int = 0
    newDocId: str = None

