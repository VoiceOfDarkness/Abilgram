from typing import List

import typesense
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, File, Form, UploadFile
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

from app.ioc import Container
from app.schemas import (
    ChatCreate,
    ChatResponse,
    MessageCreate,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services import ChatService, MessageService, UserService
from app.typesense_conf import client

router = APIRouter(prefix="/api", tags=["Chat"])


@router.get("/")
async def get_all():
    return {"message": "Hello yeblan"}


@router.post("/user", response_model=UserResponse)
@inject
async def create_user(
    user: UserCreate,
    service: UserService = Depends(Provide[Container.user_service]),
):
    return await service.create_user(user)


@router.get("/user/{supertokens_user_id}", response_model=UserResponse)
@inject
async def get_user(
    supertokens_user_id: str,
    service: UserService = Depends(Provide[Container.user_service]),
):
    return await service.get_by_supertokens_id(supertokens_user_id)


@router.patch("/user", response_model=UserResponse)
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


@router.get("/user_id")
async def get_user_id(session: SessionContainer = Depends(verify_session())):
    return {"user_id": session.get_user_id()}


@router.get("/profile", response_model=UserResponse)
@inject
async def get_profile(
    session: SessionContainer = Depends(verify_session()),
    service: UserService = Depends(Provide[Container.user_service]),
):
    return await service.get_by_supertokens_id(session.get_user_id())


@router.get("/search_user")
@inject
async def search_user(
    username: str,
    session: SessionContainer = Depends(verify_session()),
    service: UserService = Depends(Provide[Container.user_service]),
):
    return await service.search_user(username)


@router.delete("/clear_typesense")
async def clear_typesense():
    try:
        return client.collections["users"].delete()
    except typesense.exceptions.ObjectNotFound:
        return {"error": "Collections not found"}


@router.delete("/typesense/{user_id}")
async def delete_from_typesence(user_id: str):
    try:
        client.collections["users"].documents[user_id].delete()
    except Exception as e:
        return {"error": f"cannot delete due {e}"}


@router.get("/test_typesense")
async def test_typesense():
    try:
        return client.collections["users"].retrieve()
    except typesense.exceptions.ObjectNotFound:
        return {"error": "Collections not found"}


@router.post("/chat_create")
@inject
async def create_chat(
    target_user_id: str = Body(...),
    session: SessionContainer = Depends(verify_session()),
    service: ChatService = Depends(Provide[Container.chat_service]),
):
    schema = ChatCreate(
        current_user_id=session.get_user_id(), target_user_id=target_user_id
    )
    return await service.create_chat(schema)


@router.get("/chats", response_model=List[ChatResponse])
@inject
async def get_user_chats(
    session: SessionContainer = Depends(verify_session()),
    service: ChatService = Depends(Provide[Container.chat_service]),
):
    return await service.get_user_chats(session.get_user_id())


@router.get("/messages/{chat_id}")
@inject
async def get_chat_messages(
    chat_id: int,
    session: SessionContainer = Depends(verify_session()),
    service: MessageService = Depends(Provide[Container.message_service]),
):
    return await service.get_chat_messages(chat_id)


@router.delete("/delete_chat")
@inject
async def delete_user_chat(
    chat_id: int,
    session: SessionContainer = Depends(verify_session()),
    service: ChatService = Depends(Provide[Container.chat_service]),
):
    return await service.delete(chat_id)


@router.post("/send_message")
@inject
async def send_message(
    chat_id: int = Body(...),
    content: str = Body(...),
    session: SessionContainer = Depends(verify_session()),
    service: MessageService = Depends(Provide[Container.message_service]),
):
    data = MessageCreate(
        content=content, chat_id=chat_id, sender_id=session.get_user_id()
    )
    return await service.create_and_send_message(data)
