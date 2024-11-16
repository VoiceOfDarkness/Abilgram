from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserBase(BaseModel):
    supertokens_id: str
    username: Optional[str] = None
    email: EmailStr
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    supertokens_id: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


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


class ChatResponse(ChatBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    members: List[UserResponse] = []
    messages: List[MessageResponse] = []
