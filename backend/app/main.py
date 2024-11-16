from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from supertokens_python import (
    InputAppInfo,
    SupertokensConfig,
    get_all_cors_headers,
    init,
)
from supertokens_python.framework.fastapi import get_middleware
from supertokens_python.recipe import dashboard, emailpassword, session, userroles

from app import endpoints
from app.ioc import Container
from app.socket_io import sio
from app.ws_routes import ChatNamespace


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup
    container = Container()
    db = container.database()
    await db.create_db()
    app.container = container

    yield


def create_app():
    init(
        app_info=InputAppInfo(
            app_name="abilgram",
            api_domain="http://localhost:8000",
            website_domain="http://localhost:5173",
            api_base_path="/auth",
            website_base_path="/auth",
        ),
        supertokens_config=SupertokensConfig(
            connection_uri="http://supertokens:3567",
            # api_key=<API_KEY(if configured)>
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
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Content-Type"] + get_all_cors_headers(),
    )

    app.include_router(endpoints.router)

    return app


app = create_app()
