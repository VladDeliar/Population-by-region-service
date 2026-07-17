"""Bonus FastAPI service exposing the stored data over HTTP."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from pydantic import BaseModel

from app.config import Settings
from app.database import Database
from app.repository import CountryRepository


class CountrySchema(BaseModel):
    model_config = {"from_attributes": True}

    name: str
    region: str
    subregion: str | None
    population: int
    source: str


class RegionStatsSchema(BaseModel):
    region: str
    total_population: int
    largest_country: str
    largest_population: int
    smallest_country: str
    smallest_population: int


class ApiApplication:
    """Wires the FastAPI app to the database and repository."""

    def __init__(self) -> None:
        self._settings = Settings()
        self._database = Database(self._settings.database_url)
        self.app = FastAPI(title="Countries population API", lifespan=self._lifespan)
        self._register_routes()

    @asynccontextmanager
    async def _lifespan(self, _: FastAPI):
        await self._database.create_tables()
        yield
        await self._database.dispose()

    def _register_routes(self) -> None:
        @self.app.get("/countries", response_model=list[CountrySchema])
        async def countries(source: str | None = Query(default=None)):
            async with self._database.session() as session:
                repository = CountryRepository(session)
                return await repository.get_countries(source or self._settings.source)

        @self.app.get("/regions", response_model=list[RegionStatsSchema])
        async def regions(source: str | None = Query(default=None)):
            async with self._database.session() as session:
                repository = CountryRepository(session)
                stats = await repository.get_region_stats(source or self._settings.source)
            return [RegionStatsSchema(**dict(row._mapping)) for row in stats]


app = ApiApplication().app
