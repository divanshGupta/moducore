import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database.base import HospitalBase


class Category(HospitalBase):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)