import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.hospital.supplier.supplier_model import Supplier
from src.apps.hospital.supplier.supplier_repository import SupplierRepository


class SupplierNotFoundError(Exception):
    pass


class SupplierInUseError(Exception):
    """Raised when deleting a Supplier still referenced by at least one
    Medicine — surfaces ON DELETE RESTRICT as a clean domain error."""
    pass


class SupplierService:
    """
    Business logic for Supplier. Orchestrates SupplierRepository.
    Never writes SQL directly.
    """

    def __init__(self, session: AsyncSession):
        self.repository = SupplierRepository(session)

    async def create_supplier(
        self, name: str, contact_email: str | None = None, contact_phone: str | None = None
    ) -> Supplier:
        supplier = Supplier(name=name, contact_email=contact_email, contact_phone=contact_phone)
        return await self.repository.create(supplier)

    async def update_supplier(
        self,
        supplier_id: uuid.UUID,
        name: str | None = None,
        contact_email: str | None = None,
        contact_phone: str | None = None,
    ) -> Supplier:
        supplier = await self.repository.get_by_id(supplier_id)
        if supplier is None:
            raise SupplierNotFoundError(f"Supplier not found: {supplier_id}")

        if name is not None:
            supplier.name = name
        if contact_email is not None:
            supplier.contact_email = contact_email
        if contact_phone is not None:
            supplier.contact_phone = contact_phone

        return await self.repository.update(supplier)

    # async def delete_supplier(self, supplier_id: uuid.UUID) -> None:
    #     supplier = await self.repository.get_by_id(supplier_id)
    #     if supplier is None:
    #         raise SupplierNotFoundError(f"Supplier not found: {supplier_id}")

    #     try:
    #         await self.repository.delete(supplier)
    #     except IntegrityError as exc:
    #         raise SupplierInUseError(
    #             f"Cannot delete supplier '{supplier.name}': still referenced by existing medicines"
    #         ) from exc

    # capture the name before attempting the delete, not after it fails:
    async def delete_supplier(self, supplier_id: uuid.UUID) -> None:
        supplier = await self.repository.get_by_id(supplier_id)
        if supplier is None:
            raise SupplierNotFoundError(f"Supplier not found: {supplier_id}")

        supplier_name = supplier.name  # same reasoning as CategoryService

        try:
            await self.repository.delete(supplier)
        except IntegrityError as exc:
            raise SupplierInUseError(
                f"Cannot delete supplier '{supplier_name}': still referenced by existing medicines"
            ) from exc

    async def get_by_id(self, supplier_id: uuid.UUID) -> Supplier | None:
        return await self.repository.get_by_id(supplier_id)

    async def list_all(self) -> list[Supplier]:
        return await self.repository.list_all()
    

    # One addition worth flagging: for delete() on Category/Supplier, the RESTRICT constraint means Postgres will raise an IntegrityError if something still references the row. Rather than let that surface as a raw 500, I'm catching it in the service and re-raising as a domain-specific error, same pattern as the other domain exceptions — so the controller layer can map it to a 409 exactly like it maps DuplicateEmailError to 409 today.