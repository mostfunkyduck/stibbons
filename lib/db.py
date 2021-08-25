import json
from typing import Optional, Generator
import peewee
from lib import config, datatypes

db = peewee.SqliteDatabase(config.db_base_path())

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

class FeedEntry(BaseModel):
    publish_date    =   peewee.DateTimeField()
    email_from      =   peewee.CharField()
    contents        =   peewee.CharField()
    title           =   peewee.CharField()
    unique_id       =   peewee.CharField(unique=True)

def init():
    db.connect()
    db.create_tables([Coordinates, CachedForecast, FeedEntry])

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

def get_feed_entries(email_from: str) -> Generator[datatypes.FeedEntry, None, None]:
    for entry in FeedEntry.select().where(FeedEntry.email_from == email_from).order_by(FeedEntry.publish_date.desc()).limit(30).execute():
        yield datatypes.FeedEntry(
            email_from      =   entry.email_from,
            publish_date    =   entry.publish_date,
            contents        =   entry.contents,
            title           =   entry.title,
            unique_id       =   entry.unique_id
        )

def save_feed_entry(entry: datatypes.FeedEntry):
    FeedEntry.create(
       publish_date =   entry['publish_date'],
       email_from   =   entry['email_from'],
       contents     =   entry['contents'],
       title        =   entry['title'],
       unique_id    =   entry['unique_id']
    )
