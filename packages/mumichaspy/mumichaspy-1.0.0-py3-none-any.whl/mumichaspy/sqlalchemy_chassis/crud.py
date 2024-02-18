# -*- coding: utf-8 -*-
"""CRUD helpers for SQLAlchemy."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


# Generic CRUD functions ##########################################################################
# READ
async def get_list(
    db: AsyncSession, model, offset: int = None, limit: int = None, order_by: str = None
):
    """Retrieve a list of elements from database"""
    stmt = select(model)
    stmt = add_options_to_statement(stmt, offset, limit, order_by, model)
    return await get_list_statement_result(db, stmt)


async def get_element_by_id(db: AsyncSession, model, element_id):
    """Retrieve any DB element by id."""
    return await db.get(model, element_id)


async def get_list_statement_result(db: AsyncSession, stmt):
    """Execute given statement and return list of items."""
    result = await db.execute(stmt)
    item_list = result.unique().scalars().all()
    return item_list


async def get_first_statement_result(db: AsyncSession, stmt):
    """Execute given statement and return the first item."""
    result = await db.execute(stmt)
    item = result.scalar()
    return item


# DELETE
async def delete_element_by_id(db: AsyncSession, model, element_id):
    """Delete any DB element by id."""
    element = await get_element_by_id(db, model, element_id)
    if element is not None:
        await db.delete(element)
        await db.commit()
    return element


# Optional parameters #############################################################################
def set_order_by_to_statement(stmt, model, order_by):
    """Adds order by to given statement if needed."""
    if order_by is not None:
        if order_by.startswith("-"):
            stmt = stmt.order_by(getattr(model, order_by[1:]).desc())
        else:
            stmt = stmt.order_by(getattr(model, order_by))
    return stmt


def add_options_to_statement(stmt, offset, limit, order_by, model):
    """Adds options to given statement if needed: offset, limit, order_by."""
    stmt = set_order_by_to_statement(stmt, model, order_by)
    if offset is not None:
        stmt = stmt.offset(offset)
    if limit is not None:
        stmt = stmt.limit(limit)
    return stmt
