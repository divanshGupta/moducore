from src.apps.hospital.dashboard.dashboard_repository import DashboardRepository
from src.apps.hospital.dashboard.dashboard_schemas import DashboardSummary
from src.core.config.settings import get_settings


class DashboardService:
    def __init__(self, repository: DashboardRepository, purchase_service):
        self.repository = repository
        self.purchase_service = purchase_service

    async def get_summary(self) -> DashboardSummary:
        settings = get_settings()
        total_medicines = await self.repository.total_medicines()
        low_stock = await self.repository.low_stock(settings.low_stock_threshold)
        expiring_soon = await self.repository.expiring_soon(settings.expiring_soon_days)
        out_of_stock = await self.repository.out_of_stock()
        today_count, today_total = await self.purchase_service.get_today_summary()

        return DashboardSummary(
            total_medicines=total_medicines,
            low_stock_count=low_stock,
            expiring_soon_count=expiring_soon,
            out_of_stock_count=out_of_stock,
            today_purchases_count=today_count,
            today_purchases_total=today_total,
        )