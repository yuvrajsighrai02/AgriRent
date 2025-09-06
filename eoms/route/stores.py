from eoms import app
from flask import jsonify, request, session, redirect, url_for, render_template
from eoms.model.store import get_all_active_stores
from eoms.model.addres_utils import get_location, haversine, filter_nearby_stores, calculate_distance
from geopy.geocoders import Nominatim
from eoms.secret import ADDY_API_KEY
import requests
# Module to handle store routes


# Route to show all stores
@app.route('/stores')
def view_stores():
    all_stores = get_all_active_stores()
    return render_template('/shopping/store_list.html', stores=all_stores)

# Route to return stores as json
@app.route('/stores/json')
def get_stores_json():
    search_query = request.args.get('search', '')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    # Use geocoding service to get coordinates for the search query
    geolocator = Nominatim(user_agent="agrihire_app")
    location = geolocator.geocode(search_query)
    print(location)
    # Extract latitude and longitude from the location
    if lat and lon:
        lat, lon = float(lat), float(lon)
    elif location:
        lat, lon = location.latitude, location.longitude
    else:
        return jsonify({'error': 'Location not found'}), 404
    all_stores = get_all_active_stores()
    nearby_stores = filter_nearby_stores(all_stores, lat, lon)
    # Calculate distance between each store and the given lat and lon
    for store in nearby_stores:
        store_lat = store['lat']
        store_lon = store['lng']
        store['distance'] = calculate_distance(lat, lon, store_lat, store_lon)
    # Sort stores based on distance
    nearby_stores.sort(key=lambda x: x['distance'])
    return jsonify(nearby_stores)

# Fetch from Addy Post code search API
@app.route('/stores/post_code', methods=['GET'])
def search_post_code():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    api_key = ADDY_API_KEY
    url = f'https://api-nz.addysolutions.com/postcode?key={api_key}&s={query}'
    response = requests.get(url, headers={'Accept': 'application/json'})
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Error fetching data from Addy API'}), response.status_code