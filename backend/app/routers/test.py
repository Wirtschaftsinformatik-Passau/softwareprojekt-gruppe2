from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def geocode_address(street, number, postal_code, city):
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

# Example usage
latitude, longitude = geocode_address("Höllgasse", "22", "94032", "Passau")
if latitude and longitude:
    print(f"Coordinates: Latitude = {latitude}, Longitude = {longitude}")
else:
    print("Address not found or an error occurred")
