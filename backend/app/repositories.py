from contextlib import AbstractAsyncContextManager
from typing import Callable, List, Optional, Type, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import and_, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.models import Chat, Message, User

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository:
    def __init__(
        self,
        session_factory: Callable[[], AbstractAsyncContextManager[AsyncSession]],
        model: Type[ModelType],
    ) -> None:
        self.session_factory = session_factory
        self.model = model

    async def create(self, schema: CreateSchemaType) -> ModelType:
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    db_obj = self.model(**schema.model_dump())
                    session.add(db_obj)
                    await session.flush()
                    return db_obj
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="creation error") from e

    async def get_all(self) -> List[ModelType]:
        try:
            async with self.session_factory() as session:
                stmt = select(self.model)
                result = await session.execute(stmt)
                return result.scalars().all()
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="error with getting") from e

    async def get(self, id: int) -> Optional[ModelType]:
        try:
            async with self.session_factory() as session:
                stmt = select(self.model).where(self.model.id == id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500, detail=f"error to get object with id {id}"
            ) from e

    async def update(self, id: int, schema: UpdateSchemaType) -> Optional[ModelType]:

        try:
            async with self.session_factory() as session:
                async with session.begin():
                    stmt = (
                        select(self.model).where(self.model.id == id).with_for_update()
                    )
                    result = await session.execute(stmt)
                    obj = result.scalar_one_or_none()

                    if not obj:
                        raise HTTPException(
                            status_code=404, detail=f"object with id {id} not found"
                        )

                    update_data = schema.model_dump(exclude_unset=True)
                    for field, value in update_data.items():
                        setattr(obj, field, value)

                    await session.flush()
                    return obj
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500, detail=f"error updating object with id {id}"
            ) from e

    async def delete(self, id: int) -> bool:
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    stmt = (
                        select(self.model).where(self.model.id == id).with_for_update()
                    )
                    result = await session.execute(stmt)
                    obj = result.scalar_one_or_none()

                    if not obj:
                        return False

                    await session.delete(obj)
                    return True
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500, detail=f"error object deletion with id {id}"
            ) from e


class UserRepository(BaseRepository):
    def __init__(self, session_factory):
        super().__init__(session_factory, User)

    async def get_by_supertokens_id(self, id: str):
        try:
            async with self.session_factory() as session:
                stmt = select(self.model).where(self.model.supertokens_id == id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500, detail=f"error to get object with id {id}"
            ) from e

    async def update_by_supertokens_id(self, id: str, schema: UpdateSchemaType):
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    stmt = (
                        select(self.model)
                        .where(self.model.supertokens_id == id)
                        .with_for_update()
                    )
                    result = await session.execute(stmt)
                    obj = result.scalar_one_or_none()

                    if not obj:
                        raise HTTPException(
                            status_code=404, detail=f"object with id {id} not found"
                        )

                    update_data = schema.model_dump(
                        exclude_unset=True, exclude_none=True
                    )
                    for field, value in update_data.items():
                        setattr(obj, field, value)

                    await session.flush()
                    return obj
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500, detail=f"error updating object with id {id}"
            ) from e


class ChatRepository(BaseRepository):
    def __init__(self, session_factory):
        super().__init__(session_factory, Chat)

    async def create_chat(self, schema: CreateSchemaType) -> Optional[Chat]:
        try:
            async with self.session_factory() as session:
                existing_chat = await session.scalar(
                    select(Chat)
                    .options(joinedload(Chat.members), joinedload(Chat.messages))
                    .join(Chat.members)
                    .filter(
                        and_(
                            Chat.members.any(
                                User.supertokens_id == schema.current_user_id
                            ),
                            Chat.members.any(
                                User.supertokens_id == schema.target_user_id
                            ),
                        )
                    )
                    .group_by(Chat.id)
                    .having(func.count(User.supertokens_id) == 2)
                )

                if existing_chat:
                    return existing_chat

                users = await session.execute(
                    select(User).where(
                        User.supertokens_id.in_(
                            [schema.current_user_id, schema.target_user_id]
                        )
                    )
                )
                users_list = users.scalars().all()

                if len(users_list) != 2:
                    raise HTTPException(
                        status_code=404, detail="One or both users not found"
                    )

                chat = Chat(members=users_list)

                session.add(chat)
                await session.commit()

                await session.refresh(chat, ["members", "messages"])

                return chat

        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500, detail="Failed to create chat. Please try again later."
            ) from e

    async def get_user_chats(self, user_id: str) -> List[Chat]:
        try:
            async with self.session_factory() as session:
                stmt = (
                    select(Chat)
                    .options(joinedload(Chat.members), joinedload(Chat.messages))
                    .join(Chat.members)
                    .filter(Chat.members.any(User.supertokens_id == user_id))
                )
                result = await session.execute(stmt)
                return result.unique().scalars().all()
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail="Failed to get user chat. Please try again later.",
            ) from e


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
