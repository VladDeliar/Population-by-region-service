from collections.abc import Sequence

from sqlalchemy import ColumnElement, Row, String, delete, func, select
from sqlalchemy.dialects.postgresql import ARRAY, aggregate_order_by
from sqlalchemy.ext.asyncio import AsyncSession

from app.dto import CountryRecord
from app.models import Country


class CountryRepository:
    """Data access for the ``countries`` table."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def replace_for_source(self, source: str, records: Sequence[CountryRecord]) -> None:
        """Atomically replace all rows of one source with freshly parsed data."""
        async with self._session.begin():
            await self._session.execute(delete(Country).where(Country.source == source))
            self._session.add_all(
                Country(
                    name=record.name,
                    region=record.region,
                    subregion=record.subregion,
                    population=record.population,
                    source=source,
                )
                for record in records
            )

    async def get_region_stats(self, source: str) -> Sequence[Row]:
        """Aggregate per-region statistics with a single SQL query.

        The name of the largest/smallest country is taken as the first element
        of ``array_agg(name ORDER BY population DESC/ASC)``.
        """
        total_population = func.sum(Country.population)

        def first_name_by(*order: ColumnElement) -> ColumnElement[str]:
            aggregated = func.array_agg(
                aggregate_order_by(Country.name, *order), type_=ARRAY(String)
            )
            return aggregated[1]

        query = (
            select(
                Country.region,
                total_population.label("total_population"),
                first_name_by(Country.population.desc(), Country.name.asc()).label("largest_country"),
                func.max(Country.population).label("largest_population"),
                first_name_by(Country.population.asc(), Country.name.asc()).label("smallest_country"),
                func.min(Country.population).label("smallest_population"),
            )
            .where(Country.source == source)
            .group_by(Country.region)
            .order_by(total_population.desc())
        )
        result = await self._session.execute(query)
        return result.all()

    async def get_countries(self, source: str) -> Sequence[Country]:
        query = (
            select(Country)
            .where(Country.source == source)
            .order_by(Country.population.desc())
        )
        return (await self._session.execute(query)).scalars().all()
