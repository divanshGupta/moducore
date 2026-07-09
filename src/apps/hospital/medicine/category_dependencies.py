from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.session import get_db
from src.apps.hospital.medicine.category_service import CategoryService


def get_category_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CategoryService:
    return CategoryService(session)