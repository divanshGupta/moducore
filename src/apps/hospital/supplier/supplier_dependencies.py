from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.session import get_db
from src.apps.hospital.supplier.supplier_service import SupplierService


def get_supplier_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SupplierService:
    return SupplierService(session)