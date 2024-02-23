from matchmaking.tests.factories.in_memory_models import (
    CountryDataFactory,
    CityDataFactory,
    DestinationDataFactory,
    ShellDataFactory,
    ExperienceThemeMinimumRatingsDataFactory,
    ExperienceTypeDataFactory,
    ExperienceDataFactory,
    ItineraryDataFactory,
)


def test_country_data_factory():
    country = CountryDataFactory()
    assert country.name is not None


def test_city_data_factory():
    city = CityDataFactory()
    assert city.name != ""
    assert city.country is not None


def test_destination_data_factory():
    destination = DestinationDataFactory()
    assert destination.name != ""
    assert destination.primary_city is not None


def test_shell_data_factory():
    shell = ShellDataFactory()
    assert shell.destination is not None
    assert shell.flying_to_city is not None
    assert shell.flying_back_from_city is not None
    assert shell.length > 0
    assert shell.transport_duration_minutes > 0


def test_experience_theme_minimum_ratings_data_factory():
    rating = ExperienceThemeMinimumRatingsDataFactory()
    assert rating.theme is not None
    assert 1 <= rating.rating <= 5


def test_experience_type_data_factory():
    experience_type = ExperienceTypeDataFactory()
    assert experience_type.name is not None
    assert experience_type.type is not None
    assert isinstance(experience_type.affected_by_group_private, bool)


def test_experience_data_factory():
    experience = ExperienceDataFactory()
    assert len(experience.experience_types) > 0
    assert len(experience.theme_minimum_ratings) > 0
    assert len(experience.months) > 0
    assert experience.duration_minutes >= 0


def test_itinerary_data_factory():
    itinerary = ItineraryDataFactory()
    assert itinerary.shell is not None
    assert len(itinerary.experiences) > 0
    for experience in itinerary.experiences:
        assert len(experience.months) > 0
