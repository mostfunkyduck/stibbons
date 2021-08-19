import datetime
from typing import Optional
import peewee
from lib import config, datatypes

db = peewee.SqliteDatabase(config.DB_PATH)
LAST_UPDATED_FORMAT = '%Y-%m-%d:%H:%M:%S'

class BaseModel(peewee.Model):
    class Meta:
        database = db

class Coordinates(BaseModel):
    location    =   peewee.CharField()
    longitude   =   peewee.CharField()
    latitude    =   peewee.CharField()

class CachedForecast(BaseModel):
    location                =   peewee.CharField()
    forecast                =   peewee.CharField()
    last_updated            =   peewee.CharField()
    hazardous_conditions    =   peewee.CharField()

def init():
    db.connect()
    db.create_tables([Coordinates, CachedForecast])

def lookup_coordinates(location: str) -> Optional[datatypes.Coordinates]:
    '''
    Checks the database for cached location coordinates

    Arguments:
        location    -   a location to search in the database
    Returns:
        a types.coordinates dict or an empty dict if no cached coordinates were found
    '''
    try:
        coordinates = Coordinates.get(Coordinates.location == location)
        return datatypes.coordinates(coordinates.longitude, coordinates.latitude)
    except peewee.DoesNotExist:
        return None

def cache_coordinates(location: str, coordinates: datatypes.Coordinates):
    '''
    Caches the coordinates of a given string location

    Arguments:
        location    -   the location to cache
        coordinates -   the coordinates of the location
    '''
    Coordinates.create(location=location, longitude=coordinates['longitude'], latitude=coordinates['latitude'])

def lookup_cached_forecast(location: str) -> Optional[datatypes.CachedForecast]:
    try:
        cached = CachedForecast.get(CachedForecast.location == location)
        return datatypes.CachedForecast({
           'location': cached.location,
           'forecast': cached.forecast,
           'last_updated': datetime.datetime.strptime(cached.last_updated, LAST_UPDATED_FORMAT),
           'hazardous_conditions': cached.hazardous_conditions
        })
    except peewee.DoesNotExist:
        return None

def cache_forecast(location: str, forecast: str, hazardous_conditions: str):
    CachedForecast.create(
        location=location,
        forecast=forecast,
        last_updated=datetime.datetime.now().strftime(LAST_UPDATED_FORMAT),
        hazardous_conditions=hazardous_conditions
    )
