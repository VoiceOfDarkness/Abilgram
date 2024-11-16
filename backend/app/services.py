import logging
from pathlib import Path
from typing import Generic, List, Optional, TypeVar
import socketio

import aiofiles
import aiofiles.os
from fastapi import File, HTTPException
from pydantic import BaseModel

from app.models import Chat, Message, User
from app.repositories import ChatRepository, MessageRepository, UserRepository
from app.schemas import ChatCreate, MessageCreate, UserCreate, UserUpdate
from app.typesense_conf import client

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType")


logging.basicConfig(level=logging.DEBUG)


class BaseService(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, RepositoryType]
):
    def __init__(self, repository: RepositoryType) -> None:
        self.repository = repository

    async def create(self, schema: CreateSchemaType) -> ModelType:
        try:
            return await self.repository.create(schema)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Can't create an object: {str(e)}"
            )

    async def get_all(self) -> List[ModelType]:
        try:
            return await self.repository.get_all()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error to get an objects: {str(e)}"
            )

    async def get(self, id: int) -> Optional[ModelType]:
        try:
            obj = await self.repository.get(id)
            if not obj:
                raise HTTPException(
                    status_code=404, detail=f"object with id {id} not found"
                )
            return obj
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error to get an object: {str(e)}"
            )

    async def update(self, id: int, schema: UpdateSchemaType) -> ModelType:
        try:
            obj = await self.repository.update(id, schema)
            if not obj:
                raise HTTPException(
                    status_code=404, detail=f"Object with id {id} not found"
                )
            return obj
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error while updating object: {str(e)}"
            )

    async def delete(self, id: int) -> bool:
        try:
            is_deleted = await self.repository.delete(id)
            if not is_deleted:
                raise HTTPException(
                    status_code=404, detail=f"Object with id {id} not found"
                )
            return True
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error while deleting object: {str(e)}"
            )

    async def exists(self, id: int) -> bool:
        obj = await self.repository.get(id)
        return obj is not None


class UserService(
    BaseService[User, UserCreate, UserUpdate, UserRepository]
):  # User, UserCreate, UserUpdate, UserRepository # noqa
    def __init__(self, repository: UserRepository):
        super().__init__(repository)

    async def get_by_supertokens_id(self, id: str):
        try:
            return await self.repository.get_by_supertokens_id(id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error to get an object: {str(e)}"
            )

    async def update_user(self, id: str, schema: UpdateSchemaType, user_image: File):
        try:
            if user_image:
                file_path = Path("/app/media") / id / user_image.filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(await user_image.read())

            user = await self.repository.update_by_supertokens_id(id, schema)

            if user:
                typesense_data = {
                    "id": id,
                    "supertokens_id": user.supertokens_id,
                    "email": user.email,
                    "username": user.username,
                    "avatar_url": user.avatar_url or "",
                }
                client.collections["users"].documents.upsert(typesense_data)

            return user

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error to update an object: {str(e)}"
            )

    async def create_user(self, schema: CreateSchemaType) -> ModelType:
        try:
            user = await self.repository.create(schema)

            user_data = {
                "id": user.supertokens_id,
                "supertokens_id": user.supertokens_id,
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar_url or "",
            }
            client.collections["users"].documents.create(user_data)

            return user
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Can't create an object: {str(e)}"
            )

    async def search_user(self, username: str):
        try:
            result = client.collections["users"].documents.search(
                {
                    "q": username,
                    "query_by": "username",
                }
            )
            return result["hits"][0]["document"]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Can't find an object: {str(e)}"
            )


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
