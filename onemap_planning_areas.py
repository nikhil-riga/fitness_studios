import requests
import pandas as pd
import json
from typing import List, Dict, Any
import os
from config import ONEMAP_BASE_URL, ONEMAP_ACCESS_TOKEN, PLANNING_AREAS_OUTPUT

class OneMapPlanningAreasExtractor:
    def __init__(self):
        self.base_url = ONEMAP_BASE_URL
        
    def get_all_planning_areas(self) -> List[Dict[str, Any]]:
        """
        Get all planning areas from OneMap API
        """
        url = f"{self.base_url}/getAllPlanningarea"
        params = {'year': '2019'}
        headers = {'Authorization': f'Bearer {ONEMAP_ACCESS_TOKEN}'}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'SearchResults' in data:
                return data.get('SearchResults', [])
            else:
                print(f"API Error: Unexpected response format")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []
    
    def get_planning_area_names(self) -> List[str]:
        """
        Get list of planning area names
        """
        url = f"{self.base_url}/getPlanningareaNames"
        params = {'year': '2019'}
        headers = {'Authorization': f'Bearer {ONEMAP_ACCESS_TOKEN}'}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'SearchResults' in data:
                # Extract just the names from the results
                results = data.get('SearchResults', [])
                return [item.get('pln_area_n', '') for item in results if item.get('pln_area_n')]
            else:
                print(f"API Error: Unexpected response format")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []
    
    def get_planning_area_by_coordinates(self, lat: float, lng: float) -> Dict[str, Any]:
        """
        Get planning area information for specific coordinates
        """
        url = f"{self.base_url}/getPlanningarea"
        params = {
            'latitude': lat,
            'longitude': lng,
            'year': '2019'
        }
        headers = {'Authorization': f'Bearer {ONEMAP_ACCESS_TOKEN}'}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'OK':
                return data.get('result', {})
            else:
                print(f"API Error for coordinates ({lat}, {lng}): {data.get('status')}")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"Request error for coordinates ({lat}, {lng}): {e}")
            return {}
    
    def extract_polygon_coordinates(self, planning_area_data: Dict[str, Any]) -> List[List[float]]:
        """
        Extract polygon coordinates from planning area data
        """
        coordinates = []
        
        # Handle OneMap API response format
        if 'geojson' in planning_area_data:
            geojson_str = planning_area_data['geojson']
            try:
                geojson = json.loads(geojson_str)
                if geojson.get('type') == 'Polygon':
                    coordinates = geojson['coordinates'][0]  # First ring of polygon
                elif geojson.get('type') == 'MultiPolygon':
                    # For multipolygons, take the first polygon
                    coordinates = geojson['coordinates'][0][0]
            except (json.JSONDecodeError, KeyError, IndexError):
                pass
        
        elif 'coordinates' in planning_area_data:
            coordinates = planning_area_data['coordinates']
        
        return coordinates
    
    def process_planning_areas(self) -> pd.DataFrame:
        """
        Process all planning areas and extract relevant information
        """
        print("Fetching all planning areas from OneMap...")
        
        # Get all planning areas
        planning_areas = self.get_all_planning_areas()
        
        if not planning_areas:
            print("No planning areas found!")
            return pd.DataFrame()
        
        print(f"Found {len(planning_areas)} planning areas")
        
        processed_areas = []
        
        for area in planning_areas:
            # Handle OneMap API response format
            if isinstance(area, dict):
                area_name = area.get('pln_area_n', '')
                area_code = area_name.upper().replace(' ', '_') if area_name else ''
            else:
                area_name = str(area)
                area_code = area_name.upper().replace(' ', '_')
            
            # Extract polygon coordinates
            coordinates = self.extract_polygon_coordinates(area)
            
            # Calculate centroid if coordinates are available
            centroid_lat = 0
            centroid_lng = 0
            
            if coordinates:
                # Calculate simple centroid (average of all points)
                lats = [coord[1] for coord in coordinates]
                lngs = [coord[0] for coord in coordinates]
                centroid_lat = sum(lats) / len(lats)
                centroid_lng = sum(lngs) / len(lngs)
            
            processed_area = {
                'planning_area_name': area_name,
                'planning_area_code': area_code,
                'centroid_latitude': centroid_lat,
                'centroid_longitude': centroid_lng,
                'polygon_coordinates': json.dumps(coordinates) if coordinates else '',
                'total_coordinates': len(coordinates)
            }
            
            processed_areas.append(processed_area)
        
        # Convert to DataFrame
        df = pd.DataFrame(processed_areas)
        
        # Remove areas with no coordinates
        df = df[df['total_coordinates'] > 0]
        
        print(f"Processed {len(df)} planning areas with valid coordinates")
        return df
    
    def save_to_csv(self, df: pd.DataFrame, filepath: str):
        """
        Save DataFrame to CSV file
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        df.to_csv(filepath, index=False)
        print(f"Saved {len(df)} planning areas to {filepath}")

def main():
    """
    Main function to extract planning areas from OneMap
    """
    print("Starting OneMap planning areas extraction...")
    
    # Initialize extractor
    extractor = OneMapPlanningAreasExtractor()
    
    # Process all planning areas
    df = extractor.process_planning_areas()
    
    if not df.empty:
        # Save to CSV
        extractor.save_to_csv(df, PLANNING_AREAS_OUTPUT)
        
        # Print summary
        print("\nExtraction Summary:")
        print(f"Total planning areas: {len(df)}")
        print(f"Average coordinates per area: {df['total_coordinates'].mean():.1f}")
        print("\nPlanning Areas:")
        for _, row in df.iterrows():
            print(f"- {row['planning_area_name']} ({row['planning_area_code']})")
    
    return df

if __name__ == "__main__":
    main()
