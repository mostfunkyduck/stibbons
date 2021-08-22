import json
from typing import Optional
import peewee
from lib import config, datatypes

db = peewee.SqliteDatabase(config.STIBBONS_DB_PATH)

class BaseModel(peewee.Model):
    class Meta:
        database = db

class Coordinates(BaseModel):
    location    =   peewee.CharField(unique=True)
    longitude   =   peewee.CharField()
    latitude    =   peewee.CharField()

class CachedForecast(BaseModel):
    location                =   peewee.CharField(unique=True)
    forecast                =   peewee.CharField()
    feed_XML                =   peewee.CharField()

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
           'forecast': json.loads(cached.forecast),
           'feed_XML': cached.feed_XML
        })
    except peewee.DoesNotExist:
        return None

def cache_forecast(location: str, forecast: str, feed_XML: str):
    CachedForecast.insert(
        location=location,
        forecast=forecast,
        feed_XML=feed_XML
    ).on_conflict('replace').execute()
