from __future__ import annotations

from dataclasses import asdict, astuple, dataclass, field


# This data comes from the Typeform that leads fill out from our website.
# This is the variable input to every run of our matchmaking algorithm.


@dataclass(frozen=True)
class TripParameters:
    num_travellers: int  # 1-4 people
    length: int  # desired length of trip in days
    ratings: TmFormRatings  # 1-5 ratings for each category
    pace: int  # 1-5 scale, 1 being slowest
    fears_phobias_medical: list[str]  # values match FearPhobiasMedical.labels
    dietary: list[str]  # values match DietaryRequirement.labels
    location_exclusions: list[str]  # places (cities / countries)
    main_month_int: int  # corresponds to Month


@dataclass(frozen=True)
class TmFormRatings:
    outdoor: float = field(metadata={"title": "Outdoor activities"})
    nature: float = field(metadata={"title": "Relaxing in nature"})
    villages: float = field(metadata={"title": "Pretty villages"})
    sites: float = field(metadata={"title": "Popular sites"})
    history: float = field(metadata={"title": "Historical places"})
    museums_art: float = field(metadata={"title": "Museums/galleries"})
    shows: float = field(metadata={"title": "Local performances"})
    rr: float = field(metadata={"title": "Rest and relaxation"})
    wildlife: float = field(metadata={"title": "Wildlife"})
    food: float = field(metadata={"title": "Local food"})

    def __getitem__(self, key):  # type: ignore[no-untyped-def]
        return getattr(self, key)

    @property
    def normalised(self) -> TmFormRatings:
        highest_rating = max(astuple(self))
        multiplier = 5 / highest_rating
        ratings = TmFormRatings(
            outdoor=self.outdoor * multiplier,
            nature=self.nature * multiplier,
            villages=self.villages * multiplier,
            sites=self.sites * multiplier,
            history=self.history * multiplier,
            museums_art=self.museums_art * multiplier,
            shows=self.shows * multiplier,
            rr=self.rr * multiplier,
            wildlife=self.wildlife * multiplier,
            food=self.food * multiplier,
        )
        return ratings

    @property
    def normalised_rounded(self) -> TmFormRatings:
        """
        Take the output of the normalsation process above and round the values to
        the nearest whole number (but keep them as floats typing-wise).
        """

        def normal_round(number: float) -> int:
            """Round a float to the nearest integer"""
            return int(number + 0.5)

        normalised_ratings_dict = asdict(self.normalised)
        normalised_ratings_dict = {
            key: normal_round(value) for key, value in normalised_ratings_dict.items()
        }
        ratings = TmFormRatings(**normalised_ratings_dict)
        return ratings
