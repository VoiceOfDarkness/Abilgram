from app.domain.models.user import User
from app.domain.repositories.base_repository import (BaseRepository,
                                                     UpdateSchemaType)
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select


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
