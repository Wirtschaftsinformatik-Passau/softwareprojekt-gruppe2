from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def geocode_address(street, number, postal_code, city):
    """
    Geokodiert eine Adresse basierend auf Straße, Hausnummer, PLZ und Stadt.

    Args:
        street (str): Der Straßenname.
        number (str): Die Hausnummer.
        postal_code (str): Die Postleitzahl.
        city (str): Die Stadt.

    Returns:
        Tuple[float, float]: Ein Tupel mit Latitude und Longitude, wenn die Adresse gefunden wurde,
                             andernfalls (None, None).

    Example:
        latitude, longitude = geocode_address("Höllgasse", "22", "94032", "Passau")
        if latitude and longitude:
            print(f"Koordinaten: Latitude = {latitude}, Longitude = {longitude}")
        else:
            print("Adresse nicht gefunden oder ein Fehler ist aufgetreten")
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

# Example usage
latitude, longitude = geocode_address("Höllgasse", "22", "94032", "Passau")
if latitude and longitude:
    print(f"Coordinates: Latitude = {latitude}, Longitude = {longitude}")
else:
    print("Address not found or an error occurred")
