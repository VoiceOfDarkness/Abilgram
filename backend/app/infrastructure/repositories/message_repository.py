from typing import List

from app.domain.models.message import Message
from app.domain.repositories.base_repository import BaseRepository
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select


class MessageRepository(BaseRepository):
    def __init__(self, session_factory):
        super().__init__(session_factory, Message)

    async def get_chat_messages(self, chat_id: int) -> List[Message]:
        try:
            async with self.session_factory() as session:
                stmt = select(Message).where(Message.chat_id == chat_id)
                result = await session.execute(stmt)
                return result.scalars().all()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail="Failed to get chat messages. Please try again later.",
            ) from e
