import uuid
from pydantic import BaseModel, Field, ConfigDict

from src.apps.hospital.medicine.category_schemas import CategoryRead
from src.apps.hospital.supplier.supplier_schemas import SupplierRead


class MedicineCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category_id: uuid.UUID
    supplier_id: uuid.UUID


class MedicineUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category_id: uuid.UUID | None = None
    supplier_id: uuid.UUID | None = None


class MedicineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    category: CategoryRead
    supplier: SupplierRead