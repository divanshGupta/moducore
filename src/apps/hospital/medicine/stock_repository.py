import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.hospital.medicine.stock_model import Stock


class StockRepository:
    """
    Data access for Stock. Knows how to read/write `hospital.stocks`.
    Contains no business rules.

    Note: medicine eager-loading is configured on the model itself via
    relationship(lazy="selectin"), so no explicit .options() needed here.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, stock_id: uuid.UUID) -> Stock | None:
        result = await self.session.execute(select(Stock).where(Stock.id == stock_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Stock]:
        result = await self.session.execute(select(Stock).order_by(Stock.expiry_date))
        return list(result.scalars().all())

    async def list_by_medicine(self, medicine_id: uuid.UUID) -> list[Stock]:
        result = await self.session.execute(
            select(Stock)
            .where(Stock.medicine_id == medicine_id)
            .order_by(Stock.expiry_date)
        )
        return list(result.scalars().all())

    async def create(self, stock: Stock) -> Stock:
        self.session.add(stock)
        await self.session.flush()
        # Same eager-load gap as MedicineRepository — flush() only INSERTs,
        # it doesn't populate the `medicine` relationship attribute.
        return await self.get_by_id(stock.id)

    async def update(self, stock: Stock) -> Stock:
        await self.session.flush()
        return await self.get_by_id(stock.id)

    async def delete(self, stock: Stock) -> None:
        await self.session.delete(stock)
        await self.session.flush()