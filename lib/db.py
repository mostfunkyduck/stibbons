from typing import Optional
import peewee
from lib import config, datatypes

db = peewee.SqliteDatabase(config.DB_PATH)

class BaseModel(peewee.Model):
    class Meta:
        database = db

class Coordinates(BaseModel):
    location    =   peewee.CharField()
    longitude   =   peewee.CharField()
    latitude    =   peewee.CharField()

def init():
    db.connect()
    db.create_tables([Coordinates])

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
    Coordinates.create(location=location, longitude=coordinates['longitude'], latitude=coordinates['latitude'])
