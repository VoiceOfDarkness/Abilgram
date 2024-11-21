import logging
from typing import List

import socketio
from app.domain.models.chat import Chat
from app.domain.schemas.chat import ChatCreate
from app.domain.services.base_service import BaseService, CreateSchemaType
from app.infrastructure.repositories.chat_repository import ChatRepository
from fastapi import HTTPException
from pydantic import BaseModel


class ChatService(BaseService[Chat, ChatCreate, BaseModel, ChatRepository]):
    def __init__(self, repository: ChatRepository, sio: socketio.AsyncServer):
        super().__init__(repository)
        self.sio = sio

    async def create_chat(self, schema: CreateSchemaType) -> Chat:
        try:
            chat = await self.repository.create_chat(schema)

            return chat

        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Failed to create chat: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to create chat. Please try again later."
            )

    async def get_user_chats(self, user_id: str) -> List[Chat]:
        try:
            return await self.repository.get_user_chats(user_id)
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Failed to get user chat: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to get user chat. Please try again later.",
            )
