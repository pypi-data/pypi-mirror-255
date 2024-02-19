import json
import requests


def load_geojson_from_url(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad responses
    return json.loads(response.text)


def load_geojson(file_path_or_url):
    if file_path_or_url.startswith('http'):
        # If the path starts with 'http', assume it's a URL
        return load_geojson_from_url(file_path_or_url)
    else:
        with open(file_path_or_url, 'r', encoding='utf-8') as geojson_file:
            return json.load(geojson_file)


def get_coordinates(subdivision_name, geojson_path_or_url='https://raw.githubusercontent.com/srahabib/Egypt-governorates-geojson/main/Subdivisions%20of%20Egypt.json'):
    geojson_data = load_geojson(geojson_path_or_url)

    normalized_name = subdivision_name.lower().strip()

    for feature in geojson_data['features']:
        properties = feature['properties']
        geometry = feature['geometry']

        # Check both English and Arabic names
        english_name = properties.get('Subdivision_en', '').lower()
        arabic_name = properties.get('Subdivision_ar', '').lower()

        if normalized_name in [english_name, arabic_name]:
            if geometry['type'] == 'Point' and len(geometry['coordinates']) == 2:
                return tuple(geometry['coordinates'])

    # Return an empty tuple if subdivision not found
    return ()


def get_name(latitude, longitude, geojson_path_or_url='https://raw.githubusercontent.com/srahabib/Egypt-governorates-geojson/main/Subdivisions%20of%20Egypt.json'):
    geojson_data = load_geojson(geojson_path_or_url)

    for feature in geojson_data['features']:
        geometry = feature['geometry']

        if geometry['type'] == 'Point' and len(geometry['coordinates']) == 2:
            feature_latitude, feature_longitude = geometry['coordinates']

            # Set a tolerance level for coordinates matching
            tolerance = 0.0001
            if (
                abs(feature_latitude - latitude) < tolerance and
                abs(feature_longitude - longitude) < tolerance
            ):
                properties = feature['properties']
                english_name = properties.get('Subdivision_en', '')
                arabic_name = properties.get('Subdivision_ar', '')
                return f"{english_name},{arabic_name}"

    return "Location not found in the GeoJSON data."
