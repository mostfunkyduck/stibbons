'''
This lib builds properly formatted dicts for given types
'''
from typing import TypedDict, List

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

FullForecast     = TypedDict('FullForecast', {
    'url':  str,
    'hazardous_conditions': List[HazardousConditions],
    'news': List[ForecastNews],
    'forecast': Forecast,
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
    'feed_XML': str
})
