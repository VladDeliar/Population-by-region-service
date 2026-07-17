from decimal import Decimal

from app.config import Settings
from app.database import Database
from app.parsers import ParserFactory
from app.repository import CountryRepository


class GetDataService:
    """Downloads, parses and stores per-country population data."""

    def __init__(self, database: Database, settings: Settings) -> None:
        self._database = database
        self._settings = settings

    async def run(self) -> None:
        parser = ParserFactory.create(self._settings.source)
        print(f"Fetching '{parser.source_name}' data from {parser.url}")
        records = await parser.load()
        await self._database.create_tables()
        async with self._database.session() as session:
            await CountryRepository(session).replace_for_source(parser.source_name, records)
        print(f"Saved {len(records)} countries to the database.")


class PrintDataService:
    """Prints population aggregated by region, one labeled value per line."""

    _FIELDS = (
        ("Назва регіону", "region"),
        ("Загальне населення регіону", "total_population"),
        ("Назва найбільшої країни в регіоні (за населенням)", "largest_country"),
        ("Населення найбільшої країни в регіоні", "largest_population"),
        ("Назва найменшої країни в регіоні", "smallest_country"),
        ("Населення найменшої країни в регіоні", "smallest_population"),
    )

    def __init__(self, database: Database, settings: Settings) -> None:
        self._database = database
        self._settings = settings

    async def run(self) -> None:
        source = ParserFactory.create(self._settings.source).source_name
        await self._database.create_tables()
        async with self._database.session() as session:
            stats = await CountryRepository(session).get_region_stats(source)
        if not stats:
            print(f"No data for source '{source}'. Run get_data first.")
            return
        for row in stats:
            for label, field in self._FIELDS:
                value = getattr(row, field)
                # SUM(bigint) comes back from Postgres as NUMERIC → Decimal
                if isinstance(value, (int, Decimal)):
                    value = f"{value:,}"
                print(f"{label}: {value}")
            print()
