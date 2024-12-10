from contextlib import asynccontextmanager

import socketio
from app.application.api.v1 import router
from app.application.socket_io import sio
from app.core.di import Container
from app.infrastructure.ws_routes import ChatNamespace
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from supertokens_python import (InputAppInfo, SupertokensConfig,
                                get_all_cors_headers, init)
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.framework.request import BaseRequest
from supertokens_python.recipe import (dashboard, emailpassword, session,
                                       userroles)
from app.core.config import settings
from typing import Optional


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup
    container = Container()
    db = container.database()
    await db.create_db()
    app.container = container

    yield


def get_origin(request: Optional[BaseRequest]) -> str:
    if request is not None:
        origin = request.get_header("origin")
        if origin is None:
            pass
        else:
            if origin in settings.CORS_ORIGINS:
                return origin

    return settings.CORS_ORIGINS[0]


def create_app():
    init(
        app_info=InputAppInfo(
            app_name="abilgram",
            api_domain=settings.API_DOMAIN,
            origin="http://localhost:5173",
            api_base_path="/auth",
            website_base_path="/auth",
        ),
        supertokens_config=SupertokensConfig(
            connection_uri=settings.SUPERTOKENS_URI,
        ),
        framework="fastapi",
        recipe_list=[
            session.init(),
            emailpassword.init(),
            dashboard.init(admins=["abil.samedov502@gmail.com"]),
            userroles.init(),
        ],
        mode="asgi",
    )

    app = FastAPI(lifespan=lifespan)

    sio.register_namespace(ChatNamespace("/chat"))
    sio_app = socketio.ASGIApp(sio)

    app.mount("/media", StaticFiles(directory="/app/media"), name="static")

    app.add_route("/socket.io/", route=sio_app, methods=["GET", "POST"])
    app.add_websocket_route("/socket.io/", sio_app)

    app.add_middleware(get_middleware())
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Content-Type"] + get_all_cors_headers(),
    )

    app.include_router(prefix="/api/v1", router=router.routers)

    return app


app = create_app()
