from contextlib import AbstractAsyncContextManager
from typing import Callable, List, Optional, Type, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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
