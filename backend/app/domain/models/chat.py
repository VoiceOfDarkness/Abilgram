from datetime import datetime
from typing import List

from app.domain.models.association_tables import chat_members
from app.domain.models.base import Base
from app.domain.models.user import User
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
    )

    messages: Mapped[List["Message"]] = relationship("Message", back_populates="chat")
    members: Mapped[List[User]] = relationship(
        User, secondary=chat_members, back_populates="chats"
    )
