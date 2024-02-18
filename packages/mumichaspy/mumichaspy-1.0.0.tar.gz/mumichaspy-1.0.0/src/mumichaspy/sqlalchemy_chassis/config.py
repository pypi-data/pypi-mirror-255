import os


class Config:
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "SQLALCHEMY_DATABASE_URL", "sqlite+aiosqlite:///./microservice.db"
    )


config = Config()
