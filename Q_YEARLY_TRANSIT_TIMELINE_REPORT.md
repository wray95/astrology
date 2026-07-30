# Q-Series Year-by-Year Transit and Event Timeline

The Q series was expanded to a year-by-year astronomical timeline from each person's birth year, with ancient records truncated to 1800 for comparability, through 2028.

## Run

- Q people: 5,010
- Annual timeline rows: 605,085
- Planets: Saturn, Mars, Venus, Jupiter, Rahu and Ketu

For every person-year, the compressed JSONL records:

- Planet sign at the start and end of the year
- Number of sign ingresses during the year
- Retrograde days
- Stationary-proxy days using absolute speed below 0.01°/day
- Whether Saturn begins the year in the person's natal Saturn sign
- Candidate biography event count and event types recorded that year

File:

`outputs/q_yearly_transit_timeline/q_yearly_timeline.jsonl.gz`

## Important limitation

The event counts come from candidate biography-field extractions, not verified complete life histories. There are still zero Q outcome labels for wealth, poverty, rags-to-riches, success, failure or downfall. Therefore the timeline can show when planetary movements and candidate events co-occur, but it cannot yet determine what happened because of the movements.

The timeline is designed for the next stage: add verified events, then query each person's years around Saturn's pre-ingress, natal-sign, exact-return and post-sign windows while comparing Mars, Venus, Jupiter, Rahu and Ketu movements.
