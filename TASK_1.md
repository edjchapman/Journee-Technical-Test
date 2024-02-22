## Background

### Intro
- Matchmaking currently runs against the `Itinerary` Django model 
- All the possible Itineraries for a form (TripParameters) to be matched against have to be in the database in that table. 
- The filters run and a subset of the `Itinerary` are returned.

### Intro Evolved
- Due to evolving requirements, we now want a "second tier" of itineraries to be available to the matchmaking algorithm. 
- It has been decided that we'll generate this larger set of itinerary possibilities on-demand
- i.e., they won't be in the `Itinerary` database table. 
- These are to be returned by a function on `ItineraryManager`, which doesn’t exist in this codebase.
- You don't need to add it, but imagine that it returns all the possible "second tier" Itinerary instances. 
- We now will need to change our matchmaking filters to be able to run against this larger second tier of itinerary also. 
- Part of the reason for this is that we think that there will be more future flexibility in having a "non-Django" version of matchmaking that doesn't run queries against the database and is therefore more portable. 
- We want the same filters to run against these new itineraries so that the options displayed to be manually selected have gone through the exact same process as for original matchmaking.

---

## The task

- Design how this in-memory version of matchmaking will work. 
- Convert a few existing filter functions to run with this new concept.

### Here is the list of `ItineraryFilter` functions that we want converted initially:
- experience_months
- experience_fears_phobias_medical
- filter_itinerary_pace
- filter_location_exclusions

### So these existing filters do not need implementing in the new version:
- experience_theme_minimum_ratings
- experiences_dietary_requirements
- dining_experiences_solo_travellers

### Additionally:

- We want one new filter added to both 
  - this new style of filters 
  - and also the existing ORM filters: filtering for severe dietary restrictions.
- If the traveller has severe dietary restrictions, we should filter out all food-related Experiences. 
- What you need to know: the table ExperienceType contains 2 rows with the names: 'Food tour & tastings' and 'Dining experience' respectively.

### You should raise a Merge Request with your suggested solution. I will review this before we talk next.

- I'm not just judging your MR
- but also how from the existing code and this new feature requirement
- you come up with a potential approach, maybe discuss it with me, and then present your solution. 
- I'm interested in that full end-to-end process.

---

## Notes

### Data
- I've not provided any data for this task, and the output is not expected to be run, 
- but it should be theoretically working if data were supplied for the matchmaking filters to run against. 
- I can supply some data if you really want it.

### Questions
- You'll likely have questions that haven't been addressed in this brief or in code, 
- so do ask anything you think of before starting, 
- I expect there to be some.

### Expectations
- Don't spend more than a few hours on this. 
At least 2 filters should be re-implemented. 
- I've carefully chosen the set of 4 as they are all implemented slightly differently, but finishing all 4 filters is not too important. 
- Additionally the ORM version of the new filter should be implemented, but the non-ORM version is also not too important.
