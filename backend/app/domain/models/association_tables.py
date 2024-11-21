from app.domain.models.base import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Table

chat_members = Table(
    "chat_members",
    Base.metadata,
    Column(
        "supertokens_id", String, ForeignKey("users.supertokens_id", ondelete="CASCADE")
    ),
    Column("chat_id", Integer, ForeignKey("chats.id", ondelete="CASCADE")),
)
