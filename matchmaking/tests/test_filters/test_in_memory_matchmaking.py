import pytest

from matchmaking.filters.in_memory_matchmaking import InMemoryItineraryFilters
from matchmaking.tests.factories.in_memory_models import (
    ItineraryDataFactory,
    ExperienceDataFactory,
    ShellDataFactory,
    DestinationDataFactory,
    CityDataFactory,
    CountryDataFactory,
)


def test_filter_experience_months():
    itineraries = [
        ItineraryDataFactory(experiences=[ExperienceDataFactory(months=[1, 2])])
    ]

    # Month inside range
    itinerary_filter = InMemoryItineraryFilters(itineraries=itineraries)
    itinerary_filter.experience_months(1)
    assert len(itinerary_filter.itineraries) == 1

    # Outside range
    itinerary_filter = InMemoryItineraryFilters(itineraries=itineraries)
    itinerary_filter.experience_months(3)
    assert len(itinerary_filter.itineraries) == 0


def test_experience_fears_phobias_medical():
    itineraries = [
        ItineraryDataFactory(
            experiences=[ExperienceDataFactory(fears_phobias_medical=["heights"])]
        )
    ]

    # Inside range
    itinerary_filter = InMemoryItineraryFilters(itineraries=itineraries)
    itinerary_filter.experience_fears_phobias_medical(["heights"])
    assert len(itinerary_filter.itineraries) == 0

    # Outside range
    itinerary_filter = InMemoryItineraryFilters(itineraries=itineraries)
    itinerary_filter.experience_fears_phobias_medical(["spiders"])
    assert len(itinerary_filter.itineraries) == 1


def create_pace_itinerary(
    duration_minutes_per_experience, transport_duration, length_days
):
    experiences = [
        ExperienceDataFactory(duration_minutes=duration_minutes_per_experience)
        for _ in range(3)
    ]
    shell = ShellDataFactory(
        transport_duration_minutes=transport_duration, length=length_days
    )
    return ItineraryDataFactory(shell=shell, experiences=experiences)


@pytest.mark.parametrize(
    "pace, booked_time_percentage, expected_inclusion",
    [
        (1, 35, False),
        (1, 45, False),
        (2, 50, False),
        (2, 60, False),
        (3, 70, False),
        (3, 80, False),
        (4, 30, True),
        (4, 10, True),
        (5, 30, True),
        (5, 10, True),
    ],
)
def test_filter_itinerary_pace(pace, booked_time_percentage, expected_inclusion):
    # Create a dynamic itinerary based on the booked_time_percentage
    length_days = 10
    total_minutes_available = 9 * 60 * length_days
    total_experience_duration = int(
        (booked_time_percentage / 100) * total_minutes_available
    )
    itinerary = create_pace_itinerary(
        duration_minutes_per_experience=total_experience_duration // 3,
        transport_duration=total_minutes_available - total_experience_duration,
        length_days=length_days,
    )

    filter_instance = InMemoryItineraryFilters(itineraries=[itinerary])
    filter_instance.filter_itinerary_pace(pace)

    # Assertion: Check if the itinerary is correctly filtered based on the pace
    assert (len(filter_instance.itineraries) > 0) == expected_inclusion


def test_filter_location_exclusions():
    # Primary City Country
    itineraries = [
        ItineraryDataFactory(
            shell=ShellDataFactory(
                destination=DestinationDataFactory(
                    primary_city=CityDataFactory(country=CountryDataFactory(name="US"))
                )
            )
        )
    ]
    # Included
    itinerary_filter = InMemoryItineraryFilters(itineraries=itineraries)
    itinerary_filter.filter_location_exclusions(location_exclusions=["FRANCE"])
    assert len(itinerary_filter.itineraries) == 1
    # Excluded
    itinerary_filter = InMemoryItineraryFilters(itineraries=itineraries)
    itinerary_filter.filter_location_exclusions(location_exclusions=["US"])
    assert len(itinerary_filter.itineraries) == 0

    # Primary City
    itineraries = [
        ItineraryDataFactory(
            shell=ShellDataFactory(
                destination=DestinationDataFactory(
                    primary_city=CityDataFactory(name="NYC")
                )
            )
        )
    ]
    # Included
    itinerary_filter = InMemoryItineraryFilters(itineraries=itineraries)
    itinerary_filter.filter_location_exclusions(location_exclusions=["PARIS"])
    assert len(itinerary_filter.itineraries) == 1
    # Excluded
    itinerary_filter = InMemoryItineraryFilters(itineraries=itineraries)
    itinerary_filter.filter_location_exclusions(location_exclusions=["NYC"])
    assert len(itinerary_filter.itineraries) == 0

    # Flying to City
    itineraries = [
        ItineraryDataFactory(
            shell=ShellDataFactory(flying_to_city=CityDataFactory(name="NYC"))
        )
    ]
    # Included
    itinerary_filter = InMemoryItineraryFilters(itineraries=itineraries)
    itinerary_filter.filter_location_exclusions(location_exclusions=["PARIS"])
    assert len(itinerary_filter.itineraries) == 1
    # Excluded
    itinerary_filter = InMemoryItineraryFilters(itineraries=itineraries)
    itinerary_filter.filter_location_exclusions(location_exclusions=["NYC"])
    assert len(itinerary_filter.itineraries) == 0

    # Flying from City
    itineraries = [
        ItineraryDataFactory(
            shell=ShellDataFactory(flying_back_from_city=CityDataFactory(name="NYC"))
        )
    ]
    # Included
    itinerary_filter = InMemoryItineraryFilters(itineraries=itineraries)
    itinerary_filter.filter_location_exclusions(location_exclusions=["PARIS"])
    assert len(itinerary_filter.itineraries) == 1
    # Excluded
    itinerary_filter = InMemoryItineraryFilters(itineraries=itineraries)
    itinerary_filter.filter_location_exclusions(location_exclusions=["NYC"])
    assert len(itinerary_filter.itineraries) == 0
