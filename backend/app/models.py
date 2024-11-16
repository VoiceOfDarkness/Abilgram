from datetime import datetime
from typing import List, Optional

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Table,
                        Text)
from sqlalchemy.orm import Mapped, relationship

from app.database import Base

chat_members = Table(
    "chat_members",
    Base.metadata,
    Column(
        "supertokens_id", String, ForeignKey("users.supertokens_id", ondelete="CASCADE")
    ),
    Column("chat_id", Integer, ForeignKey("chats.id", ondelete="CASCADE")),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True)
    supertokens_id: Mapped[str] = Column(String(255), unique=True)
    username: Mapped[Optional[str]] = Column(String(50), unique=True)
    email: Mapped[str] = Column(String(100), unique=True)
    avatar_url: Mapped[Optional[str]] = Column(String(255))
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.now)

    messages: Mapped[List["Message"]] = relationship("Message", back_populates="sender")
    chats: Mapped[List["Chat"]] = relationship(
        "Chat", secondary=chat_members, back_populates="members"
    )


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = Column(Integer, primary_key=True)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.now)

    messages: Mapped[List["Message"]] = relationship("Message", back_populates="chat")
    members: Mapped[List[User]] = relationship(
        User, secondary=chat_members, back_populates="chats"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = Column(Integer, primary_key=True)
    chat_id: Mapped[int] = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"))
    sender_id: Mapped[str] = Column(
        String, ForeignKey("users.supertokens_id", ondelete="SET NULL"), nullable=True
    )
    # reply_to_id: Mapped[Optional[int]] = Column(
    #     Integer, ForeignKey("messages.id", ondelete="SET NULL"),
    # nullable=True
    # )
    content: Mapped[Optional[str]] = Column(Text, nullable=True)
    # maybe for future use
    # is_edited: Mapped[bool] = Column(Boolean, default=False)
    # is_deleted: Mapped[bool] = Column(Boolean, default=False)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.now)
    # edited_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)

    chat: Mapped[Chat] = relationship("Chat", back_populates="messages")
    sender: Mapped[User] = relationship("User", back_populates="messages")
    # reply_to: Mapped["Message"] = relationship("Message", remote_side=[id])
