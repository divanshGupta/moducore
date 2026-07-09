import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.hospital.supplier.supplier_model import Supplier


class SupplierRepository:
    """
    Data access for Supplier. Knows how to read/write
    `hospital.suppliers`. Contains no business rules.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, supplier_id: uuid.UUID) -> Supplier | None:
        result = await self.session.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Supplier]:
        result = await self.session.execute(select(Supplier).order_by(Supplier.name))
        return list(result.scalars().all())

    async def create(self, supplier: Supplier) -> Supplier:
        self.session.add(supplier)
        await self.session.flush()
        return supplier

    async def update(self, supplier: Supplier) -> Supplier:
        # supplier is already a tracked instance from get_by_id — mutate in
        # service, flush here. No separate "save" needed with the unit-of-work
        # pattern the session already gives you.
        await self.session.flush()
        return supplier

    async def delete(self, supplier: Supplier) -> None:
        await self.session.delete(supplier)
        await self.session.flush()