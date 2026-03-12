from geoalchemy2 import Geometry
from sqlalchemy import Computed, Date, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

import datetime

from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    cuisine: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    location = mapped_column(Geometry("POINT", srid=4326), nullable=False)


class Article(Base):
    __tablename__ = "article"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    published: Mapped[datetime.date] = mapped_column(
        Date, nullable=False, server_default=func.current_date()
    )
    search_vector = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', title || ' ' || body)", persisted=True),
    )


class Region(Base):
    __tablename__ = "region"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    boundary = mapped_column(Geometry("POLYGON", srid=4326), nullable=False)
