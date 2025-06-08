from __future__ import annotations

from datetime import datetime, UTC

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base declarative class."""


class TrendSeed(Base):
    __tablename__ = "trend_seeds"

    id: Mapped[int] = mapped_column(primary_key=True)
    phrase: Mapped[str] = mapped_column(String, unique=True)

    domains: Mapped[list["Domain"]] = relationship(back_populates="trend_seed")


class Domain(Base):
    __tablename__ = "domains"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain: Mapped[str] = mapped_column(String, unique=True, index=True)
    trend_seed_id: Mapped[int | None] = mapped_column(ForeignKey("trend_seeds.id"))
    status: Mapped[str] = mapped_column(String, default="new")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    trend_seed: Mapped[TrendSeed | None] = relationship(back_populates="domains")
    availability_checks: Mapped[list["AvailabilityCheck"]] = relationship(
        back_populates="domain"
    )
    valuations: Mapped[list["Valuation"]] = relationship(back_populates="domain")
    monitors: Mapped[list["Monitor"]] = relationship(back_populates="domain")
    backorders: Mapped[list["Backorder"]] = relationship(back_populates="domain")
    listings: Mapped[list["Listing"]] = relationship(back_populates="domain")


class AvailabilityCheck(Base):
    __tablename__ = "availability_checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))
    checked_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    available: Mapped[bool] = mapped_column(Boolean)

    domain: Mapped[Domain] = relationship(back_populates="availability_checks")


class Valuation(Base):
    __tablename__ = "valuations"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))
    service: Mapped[str] = mapped_column(String)
    value: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    domain: Mapped[Domain] = relationship(back_populates="valuations")


class Monitor(Base):
    __tablename__ = "monitors"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))
    service: Mapped[str] = mapped_column(String)
    monitor_ref: Mapped[str] = mapped_column(String)

    domain: Mapped[Domain] = relationship(back_populates="monitors")


class Backorder(Base):
    __tablename__ = "backorders"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))
    provider: Mapped[str] = mapped_column(String)
    ordered_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )

    domain: Mapped[Domain] = relationship(back_populates="backorders")


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain_id: Mapped[int] = mapped_column(ForeignKey("domains.id"))
    marketplace: Mapped[str] = mapped_column(String)
    url: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")

    domain: Mapped[Domain] = relationship(back_populates="listings")

