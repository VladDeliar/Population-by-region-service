from sqlalchemy import BigInteger, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Country(Base):
    """Raw, non-aggregated population figure for a single country."""

    __tablename__ = "countries"
    __table_args__ = (UniqueConstraint("name", "source", name="uq_country_name_source"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    region: Mapped[str] = mapped_column(String(255), index=True)
    subregion: Mapped[str | None] = mapped_column(String(255))
    population: Mapped[int] = mapped_column(BigInteger)
    source: Mapped[str] = mapped_column(String(64), index=True)
