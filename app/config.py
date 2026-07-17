from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration read from environment variables.

    ``DATABASE_URL`` — SQLAlchemy async connection string.
    ``SOURCE`` — which data source to parse and print (see app.parsers.ParserFactory).
    """

    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/population"
    source: str = "wikipedia"
