from datetime import date, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.hospital.medicine.medicine_model import Medicine
from src.apps.hospital.medicine.stock_model import Stock


class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _quantity_by_medicine_subquery(self):
        """Per-medicine total quantity across all batches. Shared by low_stock()
        and out_of_stock() so the 'current quantity' definition lives in one place."""
        return (
            select(
                Medicine.id.label("medicine_id"),
                func.coalesce(func.sum(Stock.quantity), 0).label("total_qty"),
            )
            .select_from(Medicine)
            .outerjoin(Stock, Stock.medicine_id == Medicine.id)
            .group_by(Medicine.id)
            .subquery()
        )

    async def total_medicines(self) -> int:
        result = await self.db.execute(select(func.count(Medicine.id)))
        return result.scalar_one()

    async def low_stock(self, threshold: int) -> int:
        subq = self._quantity_by_medicine_subquery()
        result = await self.db.execute(
            select(func.count()).select_from(subq).where(
                and_(subq.c.total_qty > 0, subq.c.total_qty < threshold)
            )
        )
        return result.scalar_one()

    async def out_of_stock(self) -> int:
        subq = self._quantity_by_medicine_subquery()
        result = await self.db.execute(
            select(func.count()).select_from(subq).where(subq.c.total_qty == 0)
        )
        return result.scalar_one()

    async def expiring_soon(self, within_days: int) -> int:
        """Distinct medicines with at least one non-empty batch expiring in the window.
        Excludes already-zero-quantity batches — no point flagging depleted stock as 'expiring'."""
        cutoff = date.today() + timedelta(days=within_days)
        result = await self.db.execute(
            select(func.count(func.distinct(Stock.medicine_id))).where(
                and_(
                    Stock.expiry_date >= date.today(),
                    Stock.expiry_date <= cutoff,
                    Stock.quantity > 0,
                )
            )
        )
        return result.scalar_one()