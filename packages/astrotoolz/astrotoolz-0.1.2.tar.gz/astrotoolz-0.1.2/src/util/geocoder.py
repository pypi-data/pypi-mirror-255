import requests
from typing import Tuple

class Geocoder:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.cache = {}

    def get_lat_lon(self, city: str, country: str) -> Tuple[float, float]:
        cache_key = f"{city.lower()}_{country.lower()}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]

        params = {
            'q': f'{city},{country}',
            'limit': 1,
            'appid': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if not data:
            raise ValueError(f"No data found for city: {city}, country: {country}")
        
        lat_lon = (data[0]['lat'], data[0]['lon'])
        
        # Store the result in cache
        self.cache[cache_key] = lat_lon
        
        return lat_lon


