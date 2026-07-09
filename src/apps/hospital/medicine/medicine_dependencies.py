from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.session import get_db
from src.apps.hospital.medicine.medicine_service import MedicineService


def get_medicine_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> MedicineService:
    return MedicineService(session)