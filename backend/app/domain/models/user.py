from datetime import datetime, timezone
from typing import List, Optional

from app.domain.models.association_tables import chat_members
from app.domain.models.base import Base
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supertokens_id: Mapped[str] = mapped_column(String(255), unique=True)
    username: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now
    )

    messages: Mapped[List["Message"]] = relationship("Message", back_populates="sender")
    chats: Mapped[List["Chat"]] = relationship(
        "Chat", secondary=chat_members, back_populates="members"
    )
