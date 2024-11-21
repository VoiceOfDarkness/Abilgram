from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MessageBase(BaseModel):
    content: Optional[str] = None


class MessageCreate(MessageBase):
    chat_id: int
    sender_id: str


class MessageResponse(MessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    sender_id: Optional[str]
    created_at: datetime
