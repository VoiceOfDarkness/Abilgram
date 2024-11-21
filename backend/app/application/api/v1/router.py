from app.application.api.v1.endpoints.chat import chat_router
from app.application.api.v1.endpoints.message import message_router
from app.application.api.v1.endpoints.user import user_router
from fastapi import APIRouter

routers = APIRouter()
router_list = [
    user_router,
    chat_router,
    message_router,
]

for router in router_list:
    routers.include_router(router)
