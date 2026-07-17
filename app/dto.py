from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CountryRecord:
    """A single parsed country row, independent of the storage layer."""

    name: str
    region: str
    population: int
    subregion: str | None = None
