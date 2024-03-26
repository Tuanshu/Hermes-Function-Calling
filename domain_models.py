from typing import Dict, List, Literal, Optional, Tuple, Union
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system","tool"]# "function"]
    content: Optional[str]
    function_call: Optional[Dict] = None
