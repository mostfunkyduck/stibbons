"""
Nominatim usage policy:

No heavy uses (an absolute maximum of 1 request per second).

Provide a valid HTTP Referer or User-Agent identifying the application (stock User-Agents as set by http libraries will not do).

Clearly display attribution as suitable for your medium.

Data is provided under the ODbL license which requires to share alike (although small extractions are likely to be covered by fair usage / fair dealing).
"""
from typing import Optional
from geopy.geocoders import Nominatim

from lib import constants, db, datatypes

def lookup_coordinates(location: str) -> Optional[datatypes.Coordinates]:
    '''
    Will return the long/lat of a given location
    Will try to use a cache to avoid calling nominatim, but will do the latter if it needs new ones

    Arguments
        location    -   A nominatim-compatible location to look up
    '''
    cached_coordinates = db.lookup_coordinates(location)
    if cached_coordinates:
        return cached_coordinates

    nom = Nominatim(
        user_agent = constants.APP_NAME
    )
    loc = nom.geocode(location, exactly_one=True)
    if not loc:
        return None

    coordinates = datatypes.coordinates(loc.longitude, loc.latitude)
    db.cache_coordinates(location, coordinates)
    return coordinates
