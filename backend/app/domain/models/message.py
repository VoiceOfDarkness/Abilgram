from datetime import datetime
from typing import Optional

from app.domain.models.base import Base
from app.domain.models.chat import Chat
from app.domain.models.user import User
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chats.id", ondelete="CASCADE")
    )
    sender_id: Mapped[str] = mapped_column(
        String, ForeignKey("users.supertokens_id", ondelete="SET NULL"), nullable=True
    )
    # reply_to_id: Mapped[Optional[int]] = mapped_column(
    #     Integer, ForeignKey("messages.id", ondelete="SET NULL"),
    # nullable=True
    # )
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # maybe for future use
    # is_edited: Mapped[bool] = mapped_column(Boolean, default=False)
    # is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
    )
    # edited_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    chat: Mapped[Chat] = relationship("Chat", back_populates="messages")
    sender: Mapped[User] = relationship("User", back_populates="messages")
    # reply_to: Mapped["Message"] = relationship("Message", remote_side=[id])
