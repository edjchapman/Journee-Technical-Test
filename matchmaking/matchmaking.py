from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Q, QuerySet, Sum

from .models import ExperienceThemes, Itinerary

if TYPE_CHECKING:
    from .tm_form import TmFormRatings, TripParameters


# This is a excerpt of what our matchmaking algorithm is doing


class ItineraryFilters:
    def __init__(self, qs: QuerySet[Itinerary]) -> None:
        self.qs = qs

    def _run_filter(self, query: Q) -> None:
        self.qs = self.qs.filter(query)

    def experience_months(self, main_month_int: int) -> None:
        itinerary_ids = []

        for itinerary in self.qs:
            all_experiences_in_month = True

            for experience in itinerary.experiences.all():
                if main_month_int not in experience.months:
                    all_experiences_in_month = False

            if all_experiences_in_month:
                itinerary_ids.append(itinerary.id)

        self._run_filter(query=Q(id__in=itinerary_ids))

    def experience_fears_phobias_medical(
        self, fears_phobias_medical: list[str]
    ) -> None:
        query = ~Q(experiences__fears_phobias_medical__overlap=fears_phobias_medical)

        self._run_filter(query=query)

    def experience_theme_minimum_ratings(self, ratings: TmFormRatings) -> None:
        excluded_itinerary_ids = []

        for itinerary in self.qs.all():
            for experience in itinerary.experiences.all():
                for theme_minimum_rating in experience.theme_minimum_ratings.all():
                    theme_name = ExperienceThemes(theme_minimum_rating.theme).name
                    form_rating = ratings[theme_name.lower()]
                    if form_rating < theme_minimum_rating.rating:
                        excluded_itinerary_ids.append(itinerary.id)

        self._run_filter(query=~Q(id__in=excluded_itinerary_ids))

    def experiences_dietary_requirements(self, dietary: list[str]) -> None:
        form_dietary_restrictions = set(dietary)

        excluded_itinerary_ids = set()

        for itinerary in self.qs.all():
            for experience in itinerary.experiences.all():
                if set(experience.unsuitable_for_dietary_requirement).intersection(
                    form_dietary_restrictions
                ):
                    excluded_itinerary_ids.add(itinerary.id)
                    continue

        self._run_filter(query=~Q(id__in=excluded_itinerary_ids))

    def dining_experiences_solo_travellers(self, num_travellers: int) -> None:
        excluded_itinerary_ids = set()

        if num_travellers == 1:
            # We filter out ALL dining experiences
            for itinerary in self.qs.all():
                for experience in itinerary.experiences.all():
                    foodie_types = {"Dining experience"}
                    experience_type_names = set(
                        experience.experience_types.values_list("name", flat=True)
                    )
                    if len(experience_type_names.intersection(foodie_types)) > 0:
                        excluded_itinerary_ids.add(itinerary.id)
                        continue

        self._run_filter(query=~Q(id__in=excluded_itinerary_ids))

    def filter_itinerary_pace(self, pace: int) -> None:
        suitable_itinerary_ids = []
        for itinerary in self.qs:
            total_experience_duration = itinerary.experiences.aggregate(
                total_experience_duration=Sum("duration_minutes")
            )["total_experience_duration"]

            total_booked_time = (
                total_experience_duration + itinerary.shell.transport_duration_minutes
            )
            booked_time_percentage = (
                total_booked_time / (9 * 60 * itinerary.shell.length)
            ) * 100

            if pace == 1 and booked_time_percentage < 40:
                suitable_itinerary_ids.append(itinerary.id)
            elif pace == 2 and booked_time_percentage < 55:
                suitable_itinerary_ids.append(itinerary.id)
            elif pace == 3 and booked_time_percentage < 75:
                suitable_itinerary_ids.append(itinerary.id)
            elif pace == 4 and booked_time_percentage > 20:
                suitable_itinerary_ids.append(itinerary.id)
            elif pace == 5 and booked_time_percentage > 25:
                suitable_itinerary_ids.append(itinerary.id)

        self._run_filter(query=Q(id__in=suitable_itinerary_ids))

    def filter_location_exclusions(self, location_exclusions: list[str]) -> None:
        location_exclusions = [loc.lower() for loc in location_exclusions]

        location_exclusions_query = Q()

        # We need to loop over each input string to use iexact in the query
        for location in location_exclusions:
            # fmt: off
            query = (
                ~Q(shell__destination__primary_city__name__iexact=location)
                & ~Q(shell__destination__primary_city__country__name__iexact=location)
                & ~Q(shell__flying_to_city__name__iexact=location)
                & ~Q(shell__flying_to_city__country__name__iexact=location)
                & ~Q(shell__flying_back_from_city__name__iexact=location)
                & ~Q(shell__flying_back_from_city__country__name__iexact=location)
            )
            # fmt: on

            location_exclusions_query.add(query, Q.AND)

        self._run_filter(query=query)

    def run(self, trip_params: TripParameters) -> QuerySet[Itinerary]:
        """
        Run the default set of matchmaking Itinerary filters
        """

        # Filter: experience months
        self.experience_months(
            main_month_int=trip_params.main_month_int,
        )

        # Filter: experience fears, phobias, and medical
        self.experience_fears_phobias_medical(
            fears_phobias_medical=trip_params.fears_phobias_medical,
        )

        # Filter: experience minimum ratings
        self.experience_theme_minimum_ratings(
            ratings=trip_params.ratings.normalised_rounded,
        )

        # Filter: experience dietary requirements
        self.experiences_dietary_requirements(
            dietary=trip_params.dietary,
        )

        # Filter: no dining experiences for solo travellers
        self.dining_experiences_solo_travellers(
            num_travellers=trip_params.num_travellers,
        )

        # Filter: pace by percentage of booked time
        self.filter_itinerary_pace(
            pace=trip_params.pace,
        )

        # Filter: explicitly excluded locations
        self.filter_location_exclusions(
            location_exclusions=trip_params.location_exclusions,
        )

        itineraries = self.qs

        return itineraries
