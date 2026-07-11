from fastapi import APIRouter, Depends
from typing import Annotated

from src.apps.hospital.dashboard.dashboard_dependencies import get_dashboard_service
from src.apps.hospital.dashboard.dashboard_schemas import DashboardSummary
from src.apps.hospital.dashboard.dashboard_service import DashboardService
from src.modules.user.dependencies import require_permission  

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    dependencies=[Depends(require_permission("dashboard.read"))],
)
async def get_dashboard_summary(
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DashboardSummary:
    return await service.get_summary()