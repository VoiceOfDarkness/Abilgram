from app.core.config import settings
from typesense import Client
from typesense.exceptions import ObjectAlreadyExists

client = Client(
    {
        "nodes": [
            {
                "host": settings.TYPESENSE_HOST,
                "port": settings.TYPESENSE_PORT,
                "protocol": "http",
            }
        ],
        "api_key": settings.TYPESENSE_KEY,
        "connection_timeout_seconds": 2,
    }
)

UserSchema = {
    "name": "users",
    "primary_key": "supertokens_id",
    "fields": [
        {"name": "username", "type": "string"},
        {"name": "email", "type": "string"},
        {"name": "avatar_url", "type": "string", "optional": True},
        {"name": "supertokens_id", "type": "string"},
    ],
}

try:
    client.collections.create(UserSchema)
except ObjectAlreadyExists:
    pass
