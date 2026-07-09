import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.hospital.medicine.category_model import Category
from src.apps.hospital.medicine.category_repository import CategoryRepository


class CategoryNotFoundError(Exception):
    pass


class DuplicateCategoryNameError(Exception):
    pass


class CategoryInUseError(Exception):
    """Raised when deleting a Category that's still referenced by at least
    one Medicine — surfaces the DB's ON DELETE RESTRICT as a clean domain
    error instead of a raw IntegrityError/500."""
    pass


class CategoryService:
    """
    Business logic for Category. Orchestrates CategoryRepository.
    Never writes SQL directly.
    """

    def __init__(self, session: AsyncSession):
        self.repository = CategoryRepository(session)

    async def create_category(self, name: str, description: str | None = None) -> Category:
        if await self.repository.get_by_name(name) is not None:
            raise DuplicateCategoryNameError(f"Category already exists: {name}")

        category = Category(name=name, description=description)
        return await self.repository.create(category)

    async def update_category(
        self, category_id: uuid.UUID, name: str | None = None, description: str | None = None
    ) -> Category:
        category = await self.repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(f"Category not found: {category_id}")

        if name is not None and name != category.name:
            existing = await self.repository.get_by_name(name)
            if existing is not None:
                raise DuplicateCategoryNameError(f"Category already exists: {name}")
            category.name = name

        if description is not None:
            category.description = description

        return await self.repository.update(category)

    async def delete_category(self, category_id: uuid.UUID) -> None:
        category = await self.repository.get_by_id(category_id)
        if category is None:
            raise CategoryNotFoundError(f"Category not found: {category_id}")

        # Capture before attempting delete — if the flush fails, this ORM
        # instance's attributes become expired, and touching them afterward
        # (even just to read .name for an error message) triggers a reload
        # attempt on a transaction that's already failed, raising
        # PendingRollbackError and masking the real IntegrityError.
        category_name = category.name

        try:
            await self.repository.delete(category)
        except IntegrityError as exc:
            raise CategoryInUseError(
                f"Cannot delete category '{category_name}': still referenced by existing medicines"
            ) from exc

    async def get_by_id(self, category_id: uuid.UUID) -> Category | None:
        return await self.repository.get_by_id(category_id)

    async def list_all(self) -> list[Category]:
        return await self.repository.list_all()