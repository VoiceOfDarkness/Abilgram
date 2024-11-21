from app.core.di import Container
from app.domain.schemas.user import UserCreate, UserResponse, UserUpdate
from app.infrastructure.services.user_service import UserService
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, UploadFile
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

user_router = APIRouter(tags=["User"])


@user_router.post("/user", response_model=UserResponse)
@inject
async def create_user(
    user: UserCreate,
    service: UserService = Depends(Provide[Container.user_service]),
):
    return await service.create_user(user)


@user_router.get("/user/{supertokens_user_id}", response_model=UserResponse)
@inject
async def get_user(
    supertokens_user_id: str,
    service: UserService = Depends(Provide[Container.user_service]),
):
    return await service.get_by_supertokens_id(supertokens_user_id)


@user_router.patch("/user", response_model=UserResponse)
@inject
async def update_user(
    image: UploadFile = File(None),
    username: str = Form(None),
    session: SessionContainer = Depends(verify_session()),
    service: UserService = Depends(Provide[Container.user_service]),
):
    user_id = session.get_user_id()
    user_data = UserUpdate(
        username=username, avatar_url=f"{user_id}/{image.filename}" if image else None
    )
    return await service.update_user(user_id, user_data, image)


@user_router.get("/user_id")
async def get_user_id(session: SessionContainer = Depends(verify_session())):
    return {"user_id": session.get_user_id()}


@user_router.get("/profile", response_model=UserResponse)
@inject
async def get_profile(
    session: SessionContainer = Depends(verify_session()),
    service: UserService = Depends(Provide[Container.user_service]),
):
    return await service.get_by_supertokens_id(session.get_user_id())


@user_router.get("/search_user")
@inject
async def search_user(
    username: str,
    session: SessionContainer = Depends(verify_session()),
    service: UserService = Depends(Provide[Container.user_service]),
):
    return await service.search_user(username)
