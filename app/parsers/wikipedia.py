from bs4 import BeautifulSoup

from app.dto import CountryRecord
from app.parsers.base import BaseParser


class WikipediaParser(BaseParser):
    """Parses the UN population list from a fixed Wikipedia revision.

    Table columns: Location | Population (1 July 2022) | Population (1 July 2023)
    | Change | UN Continental Region | UN Statistical Subregion.
    """

    source_name = "wikipedia"
    url = (
        "https://en.wikipedia.org/w/index.php"
        "?title=List_of_countries_by_population_(United_Nations)&oldid=1215058959"
    )

    _NAME, _POPULATION_2023, _REGION, _SUBREGION = 0, 2, 4, 5

    def parse(self, html: str) -> list[CountryRecord]:
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", class_="wikitable")
        if table is None:
            raise RuntimeError(f"No wikitable found at {self.url}")

        records = []
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 6:
                continue  # header rows
            region = cells[self._REGION].get_text(strip=True)
            if not region:
                continue  # the "World" summary row has empty region cells
            population = self._parse_population(cells[self._POPULATION_2023].get_text())
            if population is None:
                continue  # no data for this territory (listed as "N/A")
            records.append(
                CountryRecord(
                    name=self._clean_name(cells[self._NAME].get_text(" ", strip=True)),
                    region=region,
                    subregion=cells[self._SUBREGION].get_text(strip=True) or None,
                    population=population,
                )
            )
        return records
