import uuid
from sqlalchemy import String, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database.base import HospitalBase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.apps.hospital.medicine.category_model import Category
    from src.apps.hospital.supplier.supplier_model import Supplier


class Medicine(HospitalBase):
    __tablename__ = "medicines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hospital.categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("hospital.suppliers.id", ondelete="RESTRICT"),
        nullable=False,
    )

    category: Mapped["Category"] = relationship(lazy="selectin")
    supplier: Mapped["Supplier"] = relationship(lazy="selectin")