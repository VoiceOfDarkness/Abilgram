from dependency_injector import containers, providers

from app.config import settings
from app.database import Database
from app.repositories import ChatRepository, MessageRepository, UserRepository
from app.services import ChatService, MessageService, UserService
from app.socket_io import sio


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.endpoints"])

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
