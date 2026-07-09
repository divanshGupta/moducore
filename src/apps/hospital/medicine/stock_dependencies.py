from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.session import get_db
from src.apps.hospital.medicine.stock_service import StockService


def get_stock_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> StockService:
    return StockService(session)