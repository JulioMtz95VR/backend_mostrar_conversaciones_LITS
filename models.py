from pydantic import BaseModel, Field

from datetime import datetime

from typing import Optional, List 

class SingleMessage(BaseModel):
    type: str
    data: dict

class Message(BaseModel):
    sessionId: str 
    messages: List[SingleMessage]
    created_at: Optional[datetime] = None

class Conversation(BaseModel):
    sessionId: str
    