from pathlib import Path

import aiofiles
from app.core.typesense_conf import client
from app.domain.models.user import User
from app.domain.schemas.user import UserCreate, UserUpdate
from app.domain.services.base_service import (BaseService, CreateSchemaType,
                                              ModelType, UpdateSchemaType)
from app.infrastructure.repositories.user_repository import UserRepository
from fastapi import File, HTTPException


class UserService(BaseService[User, UserCreate, UserUpdate, UserRepository]):
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
