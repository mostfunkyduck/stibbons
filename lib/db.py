import json
from typing import Optional, Generator
import peewee
from lib import config, datatypes

db = peewee.SqliteDatabase(config.db_base_path())

class BaseModel(peewee.Model):
    class Meta:
        database = db

class Newsletter(BaseModel):
    from_domain =   peewee.CharField()
    target_email=   peewee.CharField()
    title       =   peewee.CharField()
    description =   peewee.CharField()
    link        =   peewee.CharField()

    class Meta:
        primary_key =   peewee.CompositeKey('from_domain', 'target_email')

class Coordinates(BaseModel):
    location    =   peewee.CharField(primary_key=True)
    longitude   =   peewee.CharField()
    latitude    =   peewee.CharField()

class CachedForecast(BaseModel):
    location                =   peewee.CharField(primary_key=True)
    forecast                =   peewee.CharField()
    feed_XML                =   peewee.CharField()

class FeedEntry(BaseModel):
    publish_date    =   peewee.DateTimeField()
    contents        =   peewee.CharField()
    title           =   peewee.CharField()
    unique_id       =   peewee.CharField(primary_key=True)
    feed            =   peewee.CharField()

class NewsletterAllowlist(BaseModel):
    email_address   =   peewee.CharField(primary_key=True)

def init():
    db.connect()
    db.create_tables([Coordinates, CachedForecast, FeedEntry, NewsletterAllowlist, Newsletter])

def add_to_allowlist(email_address: str):
    NewsletterAllowlist.get_or_create(
        email_address=email_address
    )

def get_allowlist() -> Generator[datatypes.NewsletterAllowlist, None, None]:
    for each in NewsletterAllowlist.select():
        yield datatypes.NewsletterAllowlist({
            'email_address': each.email_address
        })

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

def get_feed_entries(feed: str) -> Generator[datatypes.FeedEntry, None, None]:
    for entry in FeedEntry.select().where(FeedEntry.feed == feed).order_by(FeedEntry.publish_date.desc()).limit(30).execute():
        yield datatypes.FeedEntry(
            feed            =   entry.feed,
            publish_date    =   entry.publish_date,
            contents        =   entry.contents,
            title           =   entry.title,
            unique_id       =   entry.unique_id
        )

def save_feed_entry(entry: datatypes.FeedEntry):
    FeedEntry.create(
       feed         =   entry['feed'],
       publish_date =   entry['publish_date'],
       contents     =   entry['contents'],
       title        =   entry['title'],
       unique_id    =   entry['unique_id']
    )

def add_newsletter(newsletter: datatypes.Newsletter):
    Newsletter.create(
        title           =   newsletter['title'],
        target_email    =   newsletter['target_email'],
        from_domain     =   newsletter['from_domain'] if 'from_domain' in newsletter else '',
        description     =   newsletter['description'],
        link            =   newsletter['link']
    )

def get_newsletters(target_email: Optional[str], from_domain: Optional[str]) -> Optional[Generator[datatypes.Newsletter, None, None]]:
    if from_domain and target_email:
        newsletters = Newsletter.select().where(Newsletter.from_domain == from_domain and Newsletter.target_email == target_email).execute()
    elif from_domain:
        newsletters = Newsletter.select().where(Newsletter.from_domain == from_domain).execute()
    elif target_email:
        newsletters = Newsletter.select().where(Newsletter.target_email == target_email).execute()
    else:
        return None

    if not newsletters:
        return None


    for newsletter in newsletters:
        yield datatypes.Newsletter(
            target_email=newsletter.target_email,
            title=newsletter.title,
            from_domain=newsletter.from_domain,
            description=newsletter.description,
            link=newsletter.link
        )
