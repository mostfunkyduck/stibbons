# Location Specific Weather Forecast Atom Feeds (US Only)

# Overview

This project will take a location, look up coordinates using [nominatim](https://geopy.readthedocs.io/en/stable/#nominatim), then scrape [weather.gov](https://www.weather.gov) with those coordinates to produce a weather forecast.

# Usage

## DISCLAIMERS
1. Nominatim does not want more than 1 request/second.  See their [usage policy](https://operations.osmfoundation.org/policies/nominatim/). Be advised.
1. Not all location formats are guaranteed to work. Zip codes are a prime example - there's no mechanism built in to get them to only return US codes... yet
1. Other rough edges are sure to exist, but there's very little damage you can do (outside of potentially getting throttled to hell by exceeding the rate limit)

## CLI

The CLI tool is for testing either with static pages or with provided locations
```
pipenv run cli.py --location "baltimore,md" 
... # long forecast in JSON-ese
pipenv run cli.py --static-path ./test/sample.html
... # another long JSON forecast
```

# API

The API allows retrieving an atom feed of the current forecast for a given location.  Add the following to any reader that can parse atom and sweet feedreading goodness should ensue:
```
<stibbons.url>/rss?location=<valid location in the US>
```

See above disclaimer about location parsing still being a little janky.

Example usage in hometown, usa, with stibbons hosted on `stibbons.example.com`:

```
https://stibbons.example.com/rss?location=hometown,us
```

The original protocol was rss, hence the endpoint mismatch with the current atom feed. This will be fixed eventually.

## Feed Notes

The feed will always contain one post: the most recently published forecast. Every time the endpoint is called, it will do the following:

1. Scrape a new forecast from weather.gov (this will not scale, be wary, more caching needs to be added)
2. Determine if the previously published forecast is expired based on whether the 'last updated' info on the new forecast is different from what's in the previously published one
3. If the forecast is new, it is published **instead** of what was published previously - old forecasts are discarded
4. If the hazardous conditions advisories have changed since the last forecast, appropriate language highlighting this is added to the forecast
5. If nothing has changed, the previous feed is returned with no modifications.
