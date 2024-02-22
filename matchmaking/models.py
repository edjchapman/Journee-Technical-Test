from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import QuerySet

if TYPE_CHECKING:
    from .tm_form import TripParameters


# This data exists to support our matchmaking algorithm


class Month(models.IntegerChoices):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12


class Country(models.Model):
    # Fields
    name = models.CharField(primary_key=True, max_length=100)


class City(models.Model):
    # Relationships
    country = models.ForeignKey("matchmaking.Country", on_delete=models.PROTECT)

    # Fields
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)


class Destination(models.Model):
    # Relationships
    primary_city = models.ForeignKey("matchmaking.City", on_delete=models.PROTECT)

    # Fields
    name = models.CharField(max_length=200)


class Shell(models.Model):
    # Relationships
    destination = models.ForeignKey("matchmaking.Destination", on_delete=models.PROTECT)
    flying_to_city = models.ForeignKey(
        "matchmaking.City", on_delete=models.PROTECT, related_name="shells_flying_to_city"
    )
    flying_back_from_city = models.ForeignKey(
        "matchmaking.City", on_delete=models.PROTECT, related_name="shells_flying_back_from_city"
    )

    # Fields
    length = models.PositiveIntegerField()
    transport_duration_minutes = models.PositiveIntegerField()


class ExperienceThemes(models.TextChoices):
    OUTDOOR = "Outdoor", "Doing outdoor activities"
    NATURE = "Nature", "Relaxing in nature"
    VILLAGES = "Villages", "Wandering around charming/pretty villages"
    SITES = "Sites", "Seeing popular sites and landmarks"
    HISTORY = "History", "Going to places of historical significance"
    MUSEUMS_ART = "Museums & Art", "Visiting museums and art galleries"
    SHOWS = "Shows", "Enjoying local performances"
    RR = "R&R", "Getting some rest and relaxation"
    WILDLIFE = "Wildlife", "Seeing and interacting with wildlife in nature"
    FOOD = "Food", "Eating good local food"


class ExperienceThemeMinimumRatings(models.Model):
    """
    Used for setting minimum theme ratings for an Experience inside MM filters
    """

    # Fields
    theme = models.CharField(
        choices=ExperienceThemes.choices, max_length=20, verbose_name="Rating value"
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        verbose_name_plural = "Experience theme minimum ratings"

    def __str__(self) -> str:
        return str(f"{self.get_theme_display()}: {self.rating}")


class ExperienceType(models.Model):
    class FormExperienceExclusions(models.TextChoices):
        NATURE_WALK = "Nature walk"
        HIKING = "Hiking"
        BIKING_SEGWAY = "Biking/segway"
        BOAT_TRIPS = "Boat trips"
        SWIMMING_SNORKELING = "Swimming/snorkeling"
        KAYAKING = "Kayaking/SUP"
        RAFTING = "Rafting"
        SURFING = "Surfing"
        SCUBA_DIVING = "Scuba diving"
        CANYONING_CAVING = "Canyoning/caving"
        PARAGLIDING = "Paragliding"
        HORSE_RIDING_CAMEL_RIDING = "Horse riding/camel riding"
        WINE_TASTING = "Wine tasting"
        BREWERY_DISTILLERY_TOUR = "Brewery/distillery tour"
        SPA_TREATMENTS = "Spa treatments with physical contact"

    # Fields
    name = models.CharField(max_length=50)
    type = models.CharField(
        choices=FormExperienceExclusions.choices, max_length=50, blank=True
    )
    affected_by_group_private = models.BooleanField()

    class Meta:
        ordering = ["name"]


class Experience(models.Model):
    class FearPhobiasMedical(models.TextChoices):
        HEIGHTS = "heights", "Severe fear of heights"
        DEEP_WATER = "deep_water", "Fear of deep water (e.g. swimming in the ocean)"
        SEASICK = "seasick", "Sea sickness"
        CLAUSTROPHOBIC = "claustrophobic", "Claustrophobia"
        INSECTS_REPTILES = "insects_reptiles", "Fear of insects/reptiles"
        SWIMMING = "swimming", "Can't swim"
        STRENUOUS = "strenuous", "Unable to do prolonged physical activities"
        PREGNANT = "pregnant", "Pregnancy"
        CATS = "cats", "Fear of cats"
        DOGS = "dogs", "Fear of dogs"

    class DietaryRequirement(models.TextChoices):
        VEGETARIAN = "vegetarian", "Vegetarian"
        VEGAN = "vegan", "Vegan"
        PESCATARIAN = "pescatarian", "Pescatarian"
        HALAL_KOSHER = "halal_kosher", "Halal or Kosher"
        LACTOSE_INTOLERANT = "lactose_intolerant", "Lactose intolerant"
        GLUTEN_INTOLERANT = "gluten_intolerant", "Gluten intolerant (mild)"
        NO_ALCOHOL = "no_alcohol", "Don't drink alcohol"
        NO_RED_MEAT = "no_red_meat", "Don't eat red meat"
        NO_FISH = "no_fish", "Don't eat fish"
        NO_SHELLFISH = "no_shellfish", "Don't eat shellfish"
        OTHER_SEVERE = (
            "other_severe",
            "Other severe allergies/health conditions that affect diet",
        )

    # Relationships
    experience_types = models.ManyToManyField("matchmaking.ExperienceType")
    theme_minimum_ratings = models.ManyToManyField(
        "matchmaking.ExperienceThemeMinimumRatings"
    )

    # Fields
    months = ArrayField(
        models.PositiveIntegerField(choices=Month.choices), size=12, default=list
    )
    fears_phobias_medical = ArrayField(
        models.CharField(
            max_length=100,
            choices=FearPhobiasMedical.choices,
            verbose_name="shouldn't have this condition",
        ),
        default=list,
        blank=True,
    )
    unsuitable_for_dietary_requirement = ArrayField(
        models.CharField(max_length=20, choices=DietaryRequirement.choices),
        blank=True,
        default=list,
    )
    duration_minutes = models.PositiveIntegerField()


class ItineraryManager(models.Manager["Itinerary"]):
    def after_matchmaking_filters(
        self, trip_params: TripParameters
    ) -> QuerySet[Itinerary]:
        # This is here to prevent circular imports
        from .matchmaking import ItineraryFilters

        filters = ItineraryFilters(qs=self.model.objects.all())

        itineraries = filters.run(trip_params=trip_params)

        return itineraries


class Itinerary(models.Model):
    # Relationships
    shell = models.ForeignKey(
        "matchmaking.Shell", on_delete=models.CASCADE, related_name="itineraries"
    )
    experiences = models.ManyToManyField("matchmaking.Experience")

    # Fields
    id = models.AutoField(primary_key=True)

    # Custom managers
    objects = ItineraryManager()
