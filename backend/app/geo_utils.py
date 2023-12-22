from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def geocode_address(street, number, postal_code, city):
    """
    Geocodes an address.
    :param street: Street name
    :param number: Street number
    :param postal_code: Postal code
    :param city: City
    :return: Tuple of latitude and longitude
    """
    geolocator = Nominatim(user_agent="ToseBackend")
    query = {
        'street': f'{number} {street}',
        'postalcode': postal_code,
        'city': city,
        'country': 'Germany'
    }
    try:
        location = geolocator.geocode(query)
        if location:
            return (location.latitude, location.longitude)
        else:
            return (None, None)
    except GeocoderTimedOut:
        return (None, None)
