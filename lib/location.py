"""
Nominatim usage policy:

No heavy uses (an absolute maximum of 1 request per second).

Provide a valid HTTP Referer or User-Agent identifying the application (stock User-Agents as set by http libraries will not do).

Clearly display attribution as suitable for your medium.

Data is provided under the ODbL license which requires to share alike (although small extractions are likely to be covered by fair usage / fair dealing).
"""
from typing import Dict
from geopy.geocoders import Nominatim

from lib import constants

def lookup_coordinates(location: str) -> Dict[str, str]:
    nom = Nominatim(
        user_agent = constants.APP_NAME
    )
    loc = nom.geocode(location, exactly_one=True)
    if not loc:
        return None

    return {
        'longitude': loc.longitude,
        'latitude':  loc.latitude
    }
