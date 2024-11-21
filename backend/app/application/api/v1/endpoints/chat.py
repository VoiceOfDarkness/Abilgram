from typing import List

from app.core.di import Container
from app.domain.schemas.chat import ChatCreate, ChatResponse
from app.infrastructure.services.chat_service import ChatService
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

chat_router = APIRouter(tags=["Chat"])


@chat_router.post("/chat_create")
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


@chat_router.get("/chats", response_model=List[ChatResponse])
@inject
async def get_user_chats(
    session: SessionContainer = Depends(verify_session()),
    service: ChatService = Depends(Provide[Container.chat_service]),
):
    return await service.get_user_chats(session.get_user_id())


@chat_router.delete("/delete_chat")
@inject
async def delete_user_chat(
    chat_id: int,
    session: SessionContainer = Depends(verify_session()),
    service: ChatService = Depends(Provide[Container.chat_service]),
):
    return await service.delete(chat_id)
