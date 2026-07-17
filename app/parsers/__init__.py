from app.parsers.base import BaseParser
from app.parsers.statisticstimes import StatisticsTimesParser
from app.parsers.wikipedia import WikipediaParser


class ParserFactory:
    """Maps the ``SOURCE`` environment variable value to a parser class."""

    _parsers: dict[str, type[BaseParser]] = {
        WikipediaParser.source_name: WikipediaParser,
        StatisticsTimesParser.source_name: StatisticsTimesParser,
    }

    @classmethod
    def create(cls, source: str) -> BaseParser:
        try:
            return cls._parsers[source.strip().lower()]()
        except KeyError:
            available = ", ".join(sorted(cls._parsers))
            raise ValueError(
                f"Unknown source {source!r}. Available sources: {available}"
            ) from None


__all__ = ["BaseParser", "ParserFactory", "StatisticsTimesParser", "WikipediaParser"]
