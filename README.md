# Journee Matchmaking

## Introduction

The important models in this project are `Shell`, `Experience`, and `Itinerary`.

A `Shell` is an outline of a trip and contains some georagphic information.

An `Experience` is something to do while on a trip that we book for the travellers, and is linked to multiple Shells.

An `Itinerary` is a combination of a Shell and multiple Experiences, and a filtered list of these is the output of matchmaking.

Matchmaking is run with `Itinerary.objects.after_matchmaking_filters()`, passing in the form values for a potential Journee trip: `TripParameters`.


## Developing

Tested with Python 3.11.

`pip install requirements.txt`

`black` is used for code formatting

`mypy` is used for static analysis
