from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.session import get_db 
from src.apps.hospital.dashboard.dashboard_repository import DashboardRepository
from src.apps.hospital.dashboard.dashboard_service import DashboardService
from src.apps.hospital.purchase.purchase_dependencies import get_purchase_service


def get_dashboard_service(
    db: AsyncSession = Depends(get_db),
    purchase_service=Depends(get_purchase_service),
) -> DashboardService:
    return DashboardService(repository=DashboardRepository(db), purchase_service=purchase_service)