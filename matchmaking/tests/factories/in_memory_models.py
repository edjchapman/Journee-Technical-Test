import factory
from factory import fuzzy

from matchmaking.models import (
    CountryData,
    CityData,
    DestinationData,
    ShellData,
    ExperienceThemeMinimumRatingsData,
    ExperienceTypeData,
    ExperienceData,
    ItineraryData,
    ExperienceThemes,
)


class CountryDataFactory(factory.Factory):
    class Meta:
        model = CountryData

    name = factory.Faker("country")


class CityDataFactory(factory.Factory):
    class Meta:
        model = CityData

    country = factory.SubFactory(CountryDataFactory)
    id = factory.Sequence(lambda n: n)
    name = factory.Faker("city")


class DestinationDataFactory(factory.Factory):
    class Meta:
        model = DestinationData

    primary_city = factory.SubFactory(CityDataFactory)
    name = factory.Faker("city")


class ShellDataFactory(factory.Factory):
    class Meta:
        model = ShellData

    destination = factory.SubFactory(DestinationDataFactory)
    flying_to_city = factory.SubFactory(CityDataFactory)
    flying_back_from_city = factory.SubFactory(CityDataFactory)
    length = fuzzy.FuzzyInteger(1, 30)
    transport_duration_minutes = fuzzy.FuzzyInteger(60, 480)


class ExperienceThemeMinimumRatingsDataFactory(factory.Factory):
    class Meta:
        model = ExperienceThemeMinimumRatingsData

    theme = fuzzy.FuzzyChoice([theme.value for theme in ExperienceThemes])
    rating = fuzzy.FuzzyInteger(1, 5)


class ExperienceTypeDataFactory(factory.Factory):
    class Meta:
        model = ExperienceTypeData

    name = factory.Faker("word")
    type = fuzzy.FuzzyChoice(["Nature walk", "Hiking"])  # Add more types as needed
    affected_by_group_private = fuzzy.FuzzyChoice([True, False])


class ExperienceDataFactory(factory.Factory):
    class Meta:
        model = ExperienceData

    experience_types = factory.List(
        [factory.SubFactory(ExperienceTypeDataFactory) for _ in range(2)]
    )
    theme_minimum_ratings = factory.List(
        [factory.SubFactory(ExperienceThemeMinimumRatingsDataFactory) for _ in range(2)]
    )
    months = factory.List([fuzzy.FuzzyInteger(1, 12).fuzz() for _ in range(3)])
    fears_phobias_medical = factory.List([factory.Faker("word") for _ in range(2)])
    unsuitable_for_dietary_requirement = factory.List(
        [factory.Faker("word") for _ in range(2)]
    )
    duration_minutes = fuzzy.FuzzyInteger(30, 240)


class ItineraryDataFactory(factory.Factory):
    class Meta:
        model = ItineraryData

    shell = factory.SubFactory(ShellDataFactory)
    experiences = factory.List(
        [factory.SubFactory(ExperienceDataFactory) for _ in range(3)]
    )
