import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.hospital.medicine.category_model import Category


class CategoryRepository:
    """
    Data access for Category. Knows how to read/write
    `hospital.categories`. Contains no business rules.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, category_id: uuid.UUID) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Category | None:
        result = await self.session.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Category]:
        result = await self.session.execute(select(Category).order_by(Category.name))
        return list(result.scalars().all())

    async def create(self, category: Category) -> Category:
        self.session.add(category)
        await self.session.flush()
        return category

    async def update(self, category: Category) -> Category:
        # category is already a tracked instance from get_by_id — mutate in
        # service, flush here. No separate "save" needed with the unit-of-work
        # pattern the session already gives you.
        await self.session.flush()
        return category

    async def delete(self, category: Category) -> None:
        await self.session.delete(category)
        await self.session.flush()