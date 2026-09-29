"""The filter state contract shared by the sidebar and every tab."""

from dataclasses import dataclass, field

FILTER_WIDGET_KEYS = [
    "filter_year",
    "filter_sectors",
    "filter_countries",
    "filter_states",
    "filter_cities",
    "filter_source_types",
    "filter_priorities",
]


@dataclass
class FilterState:
    year_range: tuple[int, int]
    sectors: list[str] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)
    states: list[str] = field(default_factory=list)
    cities: list[str] = field(default_factory=list)
    source_types: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
