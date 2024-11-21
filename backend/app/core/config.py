import os

from dotenv import load_dotenv
from typing import List
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    @property
    def async_database_url(self) -> str:
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(  # noqa
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            database=self.POSTGRES_DB,
        )

    # typesense
    TYPESENSE_HOST: str = os.getenv("TYPESENSE_HOST", "http://typesense:8108")
    TYPESENSE_KEY: str = os.getenv("TYPESENSE_KEY", "xyz")
    TYPESENSE_PORT: str = os.getenv("TYPESENSE_PORT", "8108")

    # FastAPI and Supertokens
    SUPERTOKENS_URI: str = os.getenv("SUPERTOKENS_URI", "http://localhost:3567")
    API_DOMAIN: str = os.getenv(
        "API_DOMAIN_DEV" if APP_ENV == "dev" else "API_DOMAIN_PROD",
        "http://localhost:8000" if APP_ENV == "dev" else "https://api.yourdomain.com",
    )
    WEBSITE_DOMAIN: str = os.getenv(
        "WEBSITE_DOMAIN_DEV" if APP_ENV == "dev" else "WEBSITE_DOMAIN_PROD",
        "http://localhost:5173" if APP_ENV == "dev" else "https://www.yourdomain.com",
    )

    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS_DEV" if APP_ENV == "dev" else "CORS_ORIGINS_PROD",
        (
            "http://localhost:5173,http://localhost:8000"
            if APP_ENV == "dev"
            else "https://www.yourdomain.com,https://api.yourdomain.com"
        ),
    ).split(",")


settings = Settings()
