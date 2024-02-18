# -*- coding: utf-8 -*-
"""Dependencies for dependency injection."""

from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from mumichaspy.sqlalchemy_chassis.config import config

engine = create_async_engine(config.SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, future=True
)

Base = declarative_base()


async def get_db():
    """Get database."""

    db = SessionLocal()
    try:
        yield db
        await db.commit()
    except:  # noqa: E722
        await db.rollback()
    finally:
        await db.close()
