from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CountryData:
    name: str


@dataclass
class CityData:
    country: CountryData
    id: Optional[int] = None
    name: str = ""


@dataclass
class DestinationData:
    primary_city: CityData
    name: str


@dataclass
class ShellData:
    destination: DestinationData
    flying_to_city: CityData
    flying_back_from_city: CityData
    length: int
    transport_duration_minutes: int


@dataclass
class ExperienceThemeMinimumRatingsData:
    theme: str
    rating: int


@dataclass
class ExperienceTypeData:
    name: str
    type: str
    affected_by_group_private: bool


@dataclass
class ExperienceData:
    experience_types: List[ExperienceTypeData] = field(default_factory=list)
    theme_minimum_ratings: List[ExperienceThemeMinimumRatingsData] = field(
        default_factory=list
    )
    months: List[int] = field(default_factory=list)
    fears_phobias_medical: List[str] = field(default_factory=list)
    unsuitable_for_dietary_requirement: List[str] = field(default_factory=list)
    duration_minutes: int = 0


@dataclass
class ItineraryData:
    shell: ShellData
    experiences: List[ExperienceData] = field(default_factory=list)
