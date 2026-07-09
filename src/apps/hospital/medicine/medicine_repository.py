import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.hospital.medicine.medicine_model import Medicine


class MedicineRepository:
    """
    Data access for Medicine. Knows how to read/write
    `hospital.medicines`. Contains no business rules.

    Note: category/supplier eager-loading is configured on the model itself
    via relationship(lazy="selectin"), so no explicit .options() needed here —
    unlike UserRepository, where the eager-load is per-query.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, medicine_id: uuid.UUID) -> Medicine | None:
        result = await self.session.execute(
            select(Medicine).where(Medicine.id == medicine_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Medicine]:
        result = await self.session.execute(select(Medicine).order_by(Medicine.name))
        return list(result.scalars().all())

    async def search_by_name(self, query: str) -> list[Medicine]:
        result = await self.session.execute(
            select(Medicine)
            .where(Medicine.name.ilike(f"%{query}%"))
            .order_by(Medicine.name)
        )
        return list(result.scalars().all())

    # async def create(self, medicine: Medicine) -> Medicine:
    #     self.session.add(medicine)
    #     await self.session.flush()
    #     return medicine

    # async def update(self, medicine: Medicine) -> Medicine:
    #     # The medicine is fetched first, its values are changed on the loaded object, and then update() flushes those changes to the database.
    #     await self.session.flush()
    #     return medicine


    """
    This costs one extra SELECT per create/update — worth it for correctness, and at MVP scale it's not a performance concern worth optimizing away yet.
    """

    async def create(self, medicine: Medicine) -> Medicine:
        self.session.add(medicine)
        await self.session.flush()
        # flush() only INSERTs — it doesn't populate relationship attributes.
        # Re-fetch via get_by_id() so category/supplier come back eager-loaded,
        # matching what MedicineRead expects to serialize.
        return await self.get_by_id(medicine.id)

    async def update(self, medicine: Medicine) -> Medicine:
        await self.session.flush()
        # Same issue, plus a subtler one: if category_id/supplier_id changed,
        # the already-loaded `category`/`supplier` relationship objects on this
        # instance still point at the OLD related row until refreshed — SQLAlchemy
        # doesn't auto-invalidate a loaded relationship just because you changed
        # the raw FK column. Re-fetching guarantees consistency.
        return await self.get_by_id(medicine.id)

    async def delete(self, medicine: Medicine) -> None:
        await self.session.delete(medicine)
        await self.session.flush()