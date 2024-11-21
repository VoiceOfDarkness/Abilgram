from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


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
