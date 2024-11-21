from app.application.socket_io import sio
from app.core.config import settings
from app.core.database import Database
from app.infrastructure.repositories.chat_repository import ChatRepository
from app.infrastructure.repositories.message_repository import \
    MessageRepository
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.services.chat_service import ChatService
from app.infrastructure.services.message_service import MessageService
from app.infrastructure.services.user_service import UserService
from dependency_injector import containers, providers


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.application.api.v1.endpoints.user",
            "app.application.api.v1.endpoints.chat",
            "app.application.api.v1.endpoints.message",
        ]
    )

    database = providers.Singleton(Database, db_url=settings.async_database_url)

    user_repository = providers.Factory(
        UserRepository, session_factory=database.provided.session
    )

    chat_repository = providers.Factory(
        ChatRepository, session_factory=database.provided.session
    )

    message_reository = providers.Factory(
        MessageRepository, session_factory=database.provided.session
    )

    user_service = providers.Factory(UserService, repository=user_repository)
    chat_service = providers.Factory(ChatService, repository=chat_repository, sio=sio)
    message_service = providers.Factory(
        MessageService, repository=message_reository, sio=sio
    )
