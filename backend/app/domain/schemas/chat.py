from datetime import datetime
from typing import List

from app.domain.schemas.message import MessageResponse
from app.domain.schemas.user import UserResponse
from pydantic import BaseModel, ConfigDict, field_validator


class ChatBase(BaseModel):
    pass


class ChatCreate(ChatBase):
    current_user_id: str
    target_user_id: str

    @field_validator("target_user_id")
    def validate_users(cls, v: str, info):
        current_user_id = info.data.get("current_user_id")
        if current_user_id and v == current_user_id:
            raise ValueError("Cannot create chat with yourself")
        return v


class ChatResponse(ChatBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    members: List[UserResponse] = []
    messages: List[MessageResponse] = []
