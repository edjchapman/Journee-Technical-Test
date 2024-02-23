import factory
from factory import fuzzy

from matchmaking.tm_form import TmFormRatings, TripParameters


class TmFormRatingsFactory(factory.Factory):
    class Meta:
        model = TmFormRatings

    outdoor = fuzzy.FuzzyFloat(1, 5)
    nature = fuzzy.FuzzyFloat(1, 5)
    villages = fuzzy.FuzzyFloat(1, 5)
    sites = fuzzy.FuzzyFloat(1, 5)
    history = fuzzy.FuzzyFloat(1, 5)
    museums_art = fuzzy.FuzzyFloat(1, 5)
    shows = fuzzy.FuzzyFloat(1, 5)
    rr = fuzzy.FuzzyFloat(1, 5)
    wildlife = fuzzy.FuzzyFloat(1, 5)
    food = fuzzy.FuzzyFloat(1, 5)


class TripParametersFactory(factory.Factory):
    class Meta:
        model = TripParameters

    num_travellers = fuzzy.FuzzyInteger(1, 4)
    length = fuzzy.FuzzyInteger(
        1, 30
    )  # Assuming trip length can vary from 1 to 30 days
    ratings = factory.SubFactory(TmFormRatingsFactory)
    pace = fuzzy.FuzzyInteger(1, 5)
    fears_phobias_medical = factory.LazyFunction(
        lambda: ["heights", "deep_water"]
    )  # Adjust as needed
    dietary = factory.LazyFunction(
        lambda: ["vegetarian", "gluten_free"]
    )  # Adjust as needed
    location_exclusions = factory.LazyFunction(
        lambda: ["New York", "Paris"]
    )  # Example locations
    main_month_int = fuzzy.FuzzyInteger(1, 12)
