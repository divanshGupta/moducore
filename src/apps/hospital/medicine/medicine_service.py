import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.hospital.medicine.medicine_model import Medicine
from src.apps.hospital.medicine.medicine_repository import MedicineRepository
from src.apps.hospital.medicine.category_repository import CategoryRepository
from src.apps.hospital.supplier.supplier_repository import SupplierRepository


class MedicineNotFoundError(Exception):
    pass


class InvalidCategoryError(Exception):
    pass


class InvalidSupplierError(Exception):
    pass


class MedicineService:
    """
    Business logic for Medicine. Orchestrates MedicineRepository plus
    read-only checks against CategoryRepository/SupplierRepository to
    validate foreign keys before insert. Never writes SQL directly.
    """

    def __init__(self, session: AsyncSession):
        self.repository = MedicineRepository(session)
        self.category_repository = CategoryRepository(session)
        self.supplier_repository = SupplierRepository(session)

    async def create_medicine(
        self, name: str, category_id: uuid.UUID, supplier_id: uuid.UUID
    ) -> Medicine:
        if await self.category_repository.get_by_id(category_id) is None:
            raise InvalidCategoryError(f"Category not found: {category_id}")

        if await self.supplier_repository.get_by_id(supplier_id) is None:
            raise InvalidSupplierError(f"Supplier not found: {supplier_id}")

        medicine = Medicine(name=name, category_id=category_id, supplier_id=supplier_id)
        return await self.repository.create(medicine)

    async def update_medicine(
        self,
        medicine_id: uuid.UUID,
        name: str | None = None,
        category_id: uuid.UUID | None = None,
        supplier_id: uuid.UUID | None = None,
    ) -> Medicine:
        medicine = await self.repository.get_by_id(medicine_id)
        if medicine is None:
            raise MedicineNotFoundError(f"Medicine not found: {medicine_id}")

        if name is not None:
            medicine.name = name

        if category_id is not None:
            if await self.category_repository.get_by_id(category_id) is None:
                raise InvalidCategoryError(f"Category not found: {category_id}")
            medicine.category_id = category_id

        if supplier_id is not None:
            if await self.supplier_repository.get_by_id(supplier_id) is None:
                raise InvalidSupplierError(f"Supplier not found: {supplier_id}")
            medicine.supplier_id = supplier_id

        return await self.repository.update(medicine)

    async def delete_medicine(self, medicine_id: uuid.UUID) -> None:
        medicine = await self.repository.get_by_id(medicine_id)
        if medicine is None:
            raise MedicineNotFoundError(f"Medicine not found: {medicine_id}")
        await self.repository.delete(medicine)

    async def get_by_id(self, medicine_id: uuid.UUID) -> Medicine | None:
        return await self.repository.get_by_id(medicine_id)

    async def list_all(self) -> list[Medicine]:
        return await self.repository.list_all()

    async def search(self, query: str) -> list[Medicine]:
        return await self.repository.search_by_name(query)