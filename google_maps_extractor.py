import requests
import pandas as pd
import time
import json
from typing import List, Dict, Any
import os
from config import GOOGLE_MAPS_API_KEY, FITNESS_KEYWORDS, SINGAPORE_BOUNDS, SINGAPORE_SEARCH_LOCATIONS, GOOGLE_MAPS_OUTPUT

class GoogleMapsExtractor:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.locations = []
        
    def search_places(self, query: str, location: str = "Singapore") -> List[Dict[str, Any]]:
        """
        Search for places using Google Places API Text Search
        """
        url = f"{self.base_url}/textsearch/json"
        params = {
            'query': f"{query} in {location}",
            'key': self.api_key,
            'type': 'establishment'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK':
                return data.get('results', [])
            else:
                print(f"API Error for query '{query}' in {location}: {data['status']}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Request error for query '{query}' in {location}: {e}")
            return []
    
    def get_place_details(self, place_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific place
        """
        url = f"{self.base_url}/details/json"
        params = {
            'place_id': place_id,
            'key': self.api_key,
            'fields': 'name,place_id,formatted_address,geometry,rating,user_ratings_total,website,formatted_phone_number'
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK':
                return data.get('result', {})
            else:
                print(f"Details API Error for place_id '{place_id}': {data['status']}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"Details request error for place_id '{place_id}': {e}")
            return {}
    
    def extract_location_data(self, place_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant fields from place data
        """
        geometry = place_data.get('geometry', {})
        location = geometry.get('location', {})
        
        return {
            'name': place_data.get('name', ''),
            'place_id': place_data.get('place_id', ''),
            'formatted_address': place_data.get('formatted_address', ''),
            'latitude': location.get('lat', 0),
            'longitude': location.get('lng', 0),
            'rating': place_data.get('rating', 0),
            'user_ratings_total': place_data.get('user_ratings_total', 0),
            'website': place_data.get('website', ''),
            'phone_number': place_data.get('formatted_phone_number', ''),
            'search_query': place_data.get('search_query', ''),  # Track which query found this
            'search_location': place_data.get('search_location', '')  # Track which location search found this
        }
    
    def search_all_fitness_locations(self) -> pd.DataFrame:
        """
        Search for all fitness-related locations using the keyword list across multiple locations
        """
        all_locations = []
        seen_place_ids = set()
        seen_names_addresses = set()  # Additional duplicate check
        
        total_searches = len(FITNESS_KEYWORDS) * len(SINGAPORE_SEARCH_LOCATIONS)
        search_count = 0
        
        print(f"Searching for {len(FITNESS_KEYWORDS)} fitness-related keywords across {len(SINGAPORE_SEARCH_LOCATIONS)} locations...")
        print(f"Total searches to perform: {total_searches}")
        
        for keyword in FITNESS_KEYWORDS:
            print(f"\nProcessing keyword: {keyword}")
            
            for location in SINGAPORE_SEARCH_LOCATIONS:
                search_count += 1
                print(f"  Search {search_count}/{total_searches}: {keyword} in {location}")
                
                # Search for places in this location
                places = self.search_places(keyword, location)
                
                for place in places:
                    place_id = place.get('place_id')
                    
                    # Skip if we've already seen this place ID
                    if place_id in seen_place_ids:
                        continue
                    
                    # Additional duplicate check using name + address
                    name = place.get('name', '').strip().lower()
                    address = place.get('formatted_address', '').strip().lower()
                    name_address_key = f"{name}|{address}"
                    
                    if name_address_key in seen_names_addresses:
                        continue
                    
                    seen_place_ids.add(place_id)
                    seen_names_addresses.add(name_address_key)
                    
                    # Get detailed information
                    details = self.get_place_details(place_id)
                    if details:
                        # Add the search query and location that found this place
                        details['search_query'] = keyword
                        details['search_location'] = location
                        location_data = self.extract_location_data(details)
                        all_locations.append(location_data)
                    
                    # Rate limiting - be respectful to the API
                    time.sleep(0.1)
                
                # Additional delay between location searches
                time.sleep(0.3)
            
            # Additional delay between keywords
            time.sleep(0.5)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_locations)
        
        if df.empty:
            print("No locations found!")
            return df
        
        # Additional duplicate removal based on multiple criteria
        print(f"Removing duplicates from {len(df)} initial results...")
        
        # Remove exact duplicates based on place_id
        df = df.drop_duplicates(subset=['place_id'])
        print(f"After place_id deduplication: {len(df)} locations")
        
        # Remove duplicates based on name + address (case insensitive)
        df['name_address_lower'] = df['name'].str.lower() + '|' + df['formatted_address'].str.lower()
        df = df.drop_duplicates(subset=['name_address_lower'])
        df = df.drop(columns=['name_address_lower'])
        print(f"After name+address deduplication: {len(df)} locations")
        
        # Remove duplicates based on coordinates (very close locations)
        df['coord_key'] = df['latitude'].round(4).astype(str) + '|' + df['longitude'].round(4).astype(str)
        df = df.drop_duplicates(subset=['coord_key'])
        df = df.drop(columns=['coord_key'])
        print(f"After coordinate deduplication: {len(df)} locations")
        
        # Filter to Singapore only (rough bounds check)
        df = df[
            (df['latitude'] >= SINGAPORE_BOUNDS['south']) &
            (df['latitude'] <= SINGAPORE_BOUNDS['north']) &
            (df['longitude'] >= SINGAPORE_BOUNDS['west']) &
            (df['longitude'] <= SINGAPORE_BOUNDS['east'])
        ]
        
        print(f"Final result: {len(df)} unique fitness locations in Singapore")
        return df
    
    def save_to_csv(self, df: pd.DataFrame, filepath: str):
        """
        Save DataFrame to CSV file
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        df.to_csv(filepath, index=False)
        print(f"Saved {len(df)} locations to {filepath}")

def main():
    """
    Main function to extract fitness locations from Google Maps
    """
    print("Starting Google Maps fitness location extraction...")
    
    # Initialize extractor
    extractor = GoogleMapsExtractor(GOOGLE_MAPS_API_KEY)
    
    # Extract all fitness locations
    df = extractor.search_all_fitness_locations()
    
    # Save to CSV
    extractor.save_to_csv(df, GOOGLE_MAPS_OUTPUT)
    
    # Print summary
    print("\nExtraction Summary:")
    print(f"Total locations found: {len(df)}")
    print(f"Average rating: {df['rating'].mean():.2f}")
    print(f"Locations with websites: {df['website'].notna().sum()}")
    print(f"Locations with phone numbers: {df['phone_number'].notna().sum()}")
    
    return df

if __name__ == "__main__":
    main()
