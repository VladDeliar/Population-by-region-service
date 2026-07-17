from bs4 import BeautifulSoup

from app.dto import CountryRecord
from app.parsers.base import BaseParser


class StatisticsTimesParser(BaseParser):
    """Parses the countries-by-population table from statisticstimes.com.

    Data rows of ``table#table_id`` have 9 cells:
    name | population (prev. year) | rank | population (latest) | rank
    | share % | change | rank change | continent.
    """

    source_name = "statisticstimes"
    url = "https://statisticstimes.com/demographics/countries-by-population.php"

    _NAME, _POPULATION_LATEST, _REGION = 0, 3, 8
    _CELLS_PER_ROW = 9

    def parse(self, html: str) -> list[CountryRecord]:
        soup = BeautifulSoup(html, "lxml")
        table = soup.find("table", id="table_id")
        if table is None:
            raise RuntimeError(f"No table#table_id found at {self.url}")

        records = []
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) != self._CELLS_PER_ROW:
                continue  # header rows
            region = cells[self._REGION].get_text(strip=True)
            if not region:
                continue  # the "World" summary row has an empty continent cell
            population = self._parse_population(cells[self._POPULATION_LATEST].get_text())
            if population is None:
                continue  # no data for this territory
            records.append(
                CountryRecord(
                    name=self._clean_name(cells[self._NAME].get_text(" ", strip=True)),
                    region=region,
                    population=population,
                )
            )
        return records
