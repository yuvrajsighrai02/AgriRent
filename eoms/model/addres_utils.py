import requests
import math
from eoms.secret import ADDY_API_KEY
from geopy.distance import geodesic
# Module to handle address API

# Use Addy API to get coorindates of input address
def get_location(address):
    url = f'https://api-nz.addysolutions.com/validation?key={ADDY_API_KEY}&address={address}'
    response = requests.get(url)
    data = response.json()
    if data.get('address'):
        return (data['address']['latitude'], data['address']['longitude'])
    return (None, None)


# Haversine formula to calculate the distance between two geographic points.
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c  # Distance in km
    return distance

# Filter store near by
def filter_nearby_stores(stores, lat, lon, radius=300):
    nearby_stores = []
    for store in stores:
        store_lat, store_lon = float(store['lat']), float(store['lng'])
        # Calculate distance between store and searched location (in kilometers)
        distance = haversine(lat, lon, store_lat, store_lon)
        if distance <= radius:
            nearby_stores.append(store)
    return nearby_stores

# Function to calculate distance between 2 points
def calculate_distance(lat1, lon1, lat2, lon2):
    # Use geodesic function from geopy to calculate distance between two points
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers