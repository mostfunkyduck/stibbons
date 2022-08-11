'''
This lib builds properly formatted dicts for given types
'''
from typing import TypedDict, List
import datetime

### Forecast Types
ForecastNews = TypedDict('ForecastNews',  {
    'headline': str,
    'body': str,
    'details_link': str
})

HazardousConditions = TypedDict('HazardousConditions', {
    'condition': str,
    'details_link': str
})

DailyForecast = TypedDict('DailyForecast', {
    'period': str,
    'description': str,
    'short_description': str,
    'temperature': str
})
Forecast = TypedDict('Forecast', {
    'title': str,
    'current_headlines': List[str],
    'current_hazards': List[str],
    'daily_forecasts': List[DailyForecast]
})

CurrentConditions = TypedDict('CurrentConditions', {
    'current_temperature': str,
    'current_conditions': str
})
FullForecast     = TypedDict('FullForecast', {
    'url':  str,
    'hazardous_conditions': List[HazardousConditions],
    'news': List[ForecastNews],
    'forecast': Forecast,
    'current_conditions': CurrentConditions,
    'last_updated': str
})

### General DataTypes
Coordinates = TypedDict('Coordinates', {'longitude': str, 'latitude': str})
def coordinates(longitude: str, latitude: str) -> Coordinates:
    return {
        'longitude': longitude,
        'latitude': latitude
    }

CachedForecast = TypedDict('CachedForecast', {
    'location': str,
    'forecast': FullForecast,
    'feed_XML': str,
    'cache_time': datetime.datetime
})

FeedEntry    = TypedDict('FeedEntry',  {
    'publish_date': datetime.datetime,
    'contents':     str,
    'title':        str,
    'unique_id':    str,
    'feed_id':      str
})

Feed         = TypedDict('Feed', {
    'feed_id':      str,
    'title':        str,
    'description':  str,
    'link':         str
})

Newsletter          = TypedDict('Newsletter', {
    'target_email': str,
    'from_domain':  str,
    'feed':         Feed
})
