from typing import List

from matchmaking.models import ItineraryData
from matchmaking.tm_form import TripParameters


class InMemoryItineraryFilters:
    def __init__(self, itineraries: List[ItineraryData]):
        self.itineraries = itineraries

    def experience_months(self, main_month_int: int) -> None:
        filtered_itineraries = []

        for itinerary in self.itineraries:
            all_experiences_in_month = True

            for experience in itinerary.experiences:
                if main_month_int not in experience.months:
                    all_experiences_in_month = False

            if all_experiences_in_month:
                filtered_itineraries.append(itinerary)

        self.itineraries = filtered_itineraries

    def experience_fears_phobias_medical(
        self, fears_phobias_medical: List[str]
    ) -> None:
        fears_phobias_medical_set = set(fears_phobias_medical)

        self.itineraries = [
            itinerary
            for itinerary in self.itineraries
            if not any(
                fears_phobias_medical_set.intersection(experience.fears_phobias_medical)
                for experience in itinerary.experiences
            )
        ]

    def filter_itinerary_pace(self, pace: int) -> None:
        suitable_itineraries = []
        for itinerary in self.itineraries:
            total_experience_duration = sum(
                [e.duration_minutes for e in itinerary.experiences]
            )

            total_booked_time = (
                total_experience_duration + itinerary.shell.transport_duration_minutes
            )

            booked_time_percentage = (
                total_booked_time / (9 * 60 * itinerary.shell.length)
            ) * 100

            if pace == 1 and booked_time_percentage < 40:
                suitable_itineraries.append(itinerary)
            elif pace == 2 and booked_time_percentage < 55:
                suitable_itineraries.append(itinerary)
            elif pace == 3 and booked_time_percentage < 75:
                suitable_itineraries.append(itinerary)
            elif pace == 4 and booked_time_percentage > 20:
                suitable_itineraries.append(itinerary)
            elif pace == 5 and booked_time_percentage > 25:
                suitable_itineraries.append(itinerary)

        self.itineraries = suitable_itineraries

    def filter_location_exclusions(self, location_exclusions: list[str]) -> None:
        location_exclusions_set = set(loc.lower() for loc in location_exclusions)

        def is_excluded(itinerary) -> bool:
            relevant_locations = {
                itinerary.shell.destination.primary_city.name.lower(),
                itinerary.shell.destination.primary_city.country.name.lower(),
                itinerary.shell.flying_to_city.name.lower(),
                itinerary.shell.flying_to_city.country.name.lower(),
                itinerary.shell.flying_back_from_city.name.lower(),
                itinerary.shell.flying_back_from_city.country.name.lower(),
            }
            return any(
                location in location_exclusions_set for location in relevant_locations
            )

        self.itineraries = [
            itinerary for itinerary in self.itineraries if not is_excluded(itinerary)
        ]

    def run(self, trip_params: TripParameters) -> List[ItineraryData]:
        """
        Run the default set of matchmaking Itinerary filters
        """

        # Filter: experience months
        self.experience_months(
            main_month_int=trip_params.main_month_int,
        )

        # Filter: pace by percentage of booked time
        self.filter_itinerary_pace(
            pace=trip_params.pace,
        )

        # Filter: explicitly excluded locations
        self.filter_location_exclusions(
            location_exclusions=trip_params.location_exclusions,
        )

        itineraries = self.itineraries

        return itineraries
