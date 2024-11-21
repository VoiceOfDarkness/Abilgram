from typing import Generic, List, Optional, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
RepositoryType = TypeVar("RepositoryType")


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
