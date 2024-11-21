from typing import List, Optional

from app.domain.models.chat import Chat
from app.domain.models.user import User
from app.domain.repositories.base_repository import (BaseRepository,
                                                     CreateSchemaType)
from fastapi import HTTPException
from sqlalchemy import and_, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


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
