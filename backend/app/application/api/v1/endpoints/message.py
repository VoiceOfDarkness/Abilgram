from app.core.di import Container
from app.domain.schemas.message import MessageCreate, MessageResponse
from app.infrastructure.services.message_service import MessageService
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends
from supertokens_python.recipe.session import SessionContainer
from supertokens_python.recipe.session.framework.fastapi import verify_session

message_router = APIRouter(tags=["Message"])


@message_router.get("/messages/{chat_id}", response_model=list[MessageResponse])
@inject
async def get_chat_messages(
    chat_id: int,
    session: SessionContainer = Depends(verify_session()),
    service: MessageService = Depends(Provide[Container.message_service]),
):
    return await service.get_chat_messages(chat_id)


@message_router.post("/send_message")
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
