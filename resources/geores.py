from geopy.geocoders import Nominatim
from geopy import distance
import config

geo = Nominatim(user_agent=config.USER_AGENT, timeout=3)


async def detecting_city(city: str = None, location: tuple = None):
    loc = None

    if city is not None:
        loc = geo.geocode(city, addressdetails=True, language='ru')

    elif location is not None:
        loc = geo.reverse(location, addressdetails=True, language='ru')

    if loc is None:
        return None
    address = loc.raw['address']
    if address.get('city') is None:
        if address.get('town') is None:
            if address.get('city_district') is None:
                if address.get('county') is None:
                    if address.get('state') is not None:
                        city = address['state']
                else:
                    city = address['county']
            else:
                city = address['city_district']
        else:
            city = address['town']
    else:
        city = address['city']
    if not address.get('state'):
        address['state'] = city
    return city, address['state'], address['country'], (loc.latitude, loc.longitude)


# for DB.py
def decode_coordinates(xyz: str):
    coordinates = xyz.split(', ')
    return float(coordinates[0]), float(coordinates[1])


def distancing(first_lo_la: str, fetched_records: list):
    for i in fetched_records:
        yield int(distance.distance(decode_coordinates(first_lo_la), decode_coordinates(dict(i)['coordinates'])).km), \
              dict(i)['id']
