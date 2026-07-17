import re
from abc import ABC, abstractmethod
from typing import ClassVar

import aiohttp

from app.dto import CountryRecord


class BaseParser(ABC):
    """Downloads a page and turns it into a list of ``CountryRecord``."""

    source_name: ClassVar[str]
    url: ClassVar[str]

    # Some sources (statisticstimes.com) reject requests without a browser UA.
    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
    }
    _TIMEOUT = aiohttp.ClientTimeout(total=60)

    async def load(self) -> list[CountryRecord]:
        html = await self._fetch()
        records = self.parse(html)
        if not records:
            raise RuntimeError(
                f"No countries parsed from {self.url} — the page layout may have changed"
            )
        return records

    async def _fetch(self) -> str:
        async with aiohttp.ClientSession(headers=self._HEADERS, timeout=self._TIMEOUT) as session:
            async with session.get(self.url) as response:
                response.raise_for_status()
                return await response.text()

    @abstractmethod
    def parse(self, html: str) -> list[CountryRecord]:
        """Extract per-country records from the raw page HTML."""

    @staticmethod
    def _clean_name(text: str) -> str:
        """Drop footnote markers like ``[a]`` and normalize whitespace."""
        name = re.sub(r"\s+", " ", re.sub(r"\[[^\]]*\]", "", text)).strip()
        return re.sub(r"\(\s+", "(", re.sub(r"\s+\)", ")", name))

    @staticmethod
    def _parse_population(text: str) -> int | None:
        """Return the population as an int, or None when the cell has no number
        (e.g. Pitcairn Islands is listed as "N/A" on Wikipedia)."""
        digits = re.sub(r"\D", "", text)
        return int(digits) if digits else None
