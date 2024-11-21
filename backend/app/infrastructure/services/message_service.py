import logging
from typing import List

import socketio
from app.domain.models.message import Message
from app.domain.schemas.message import BaseModel, MessageCreate
from app.domain.services.base_service import BaseService, CreateSchemaType
from app.infrastructure.repositories.message_repository import \
    MessageRepository
from fastapi import HTTPException


class MessageService(BaseService[Message, MessageCreate, BaseModel, MessageRepository]):
    def __init__(self, repository: MessageRepository, sio: socketio.AsyncServer):
        super().__init__(repository)
        self.sio = sio

    async def create_and_send_message(self, schema: CreateSchemaType) -> Message:
        try:
            message = await self.repository.create(schema)

            return message

        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Failed to create message: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create message. Please try again later.",
            )

    async def get_chat_messages(self, chat_id: int) -> List[Message]:
        try:
            return await self.repository.get_chat_messages(chat_id)
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Failed to get chat messages: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get chat messages. Please try again later.",
            )
