# Overview

This project will take a location, look up coordinates using [nominatim](https://geopy.readthedocs.io/en/stable/#nominatim), then scrape [weather.gov](https://www.weather.gov) with those coordinates to produce a weather forecast

# Usage

## DISCLAIMERS
1. Nominatim does not want more than 1 request/second.  See their [usage policy](https://operations.osmfoundation.org/policies/nominatim/). Be advised.
1. This is still early stages, not all location formats are guaranteed to work. Zip codes are a prime example - there's no mechanism built in to get them to only return US codes... yet
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

The flask API allows you to look up locations and get forecasts dynamically

Start it by simply running 
```
pipenv run start-api.py
```

Call it like so:
```
curl localhost:5000/api/v1/forecast?location=Baltimore,MD
```

# API Docs/Schema
Soon to come...
