import requests
import pandas as pd
import json
import time
from typing import List, Dict, Any
import os
from config import ONEMAP_BASE_URL, ONEMAP_ACCESS_TOKEN, INCOME_DATA_OUTPUT

class OneMapIncomeDataExtractor:
    def __init__(self):
        self.base_url = ONEMAP_BASE_URL
        
    def get_household_income_data(self, planning_area: str, year: str = "2020") -> Dict[str, Any]:
        """
        Get household income data for a specific planning area
        """
        url = f"{self.base_url}/getHouseholdMonthlyIncomeWork"
        params = {
            'planningArea': planning_area,
            'year': year
        }
        headers = {'Authorization': f'Bearer {ONEMAP_ACCESS_TOKEN}'}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Income API returns a list directly, not an object with status
            if isinstance(data, list) and len(data) > 0:
                return data[0]  # Return the first (and only) result
            else:
                print(f"API Error for {planning_area}: No data returned")
                return {}
                
        except requests.exceptions.RequestException as e:
            print(f"Request error for {planning_area}: {e}")
            return {}
    
    def calculate_income_midpoint(self, income_range: str) -> float:
        """
        Calculate the midpoint of an income range
        """
        # Remove 'sgd_' prefix and convert to lowercase
        range_str = income_range.replace('sgd_', '').lower()
        
        if range_str == '20000_over':
            return 20000.0
        
        # Handle ranges like '10000_to_10999'
        if 'to' in range_str:
            parts = range_str.split('_to_')
            if len(parts) == 2:
                try:
                    lower = float(parts[0])
                    upper = float(parts[1])
                    return (lower + upper) / 2
                except ValueError:
                    return 0.0
        
        # Handle ranges like '1000_to_1999'
        if 'to' in range_str:
            parts = range_str.split('_to_')
            if len(parts) == 2:
                try:
                    lower = float(parts[0])
                    upper = float(parts[1])
                    return (lower + upper) / 2
                except ValueError:
                    return 0.0
        
        # Handle single values like '1000'
        try:
            return float(range_str)
        except ValueError:
            return 0.0
    
    def calculate_weighted_average_income(self, income_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate weighted average income from income distribution data
        """
        total_households = 0
        weighted_sum = 0.0
        
        # Income ranges and their counts
        income_ranges = {}
        
        for key, count in income_data.items():
            if key.startswith('sgd_') and isinstance(count, (int, float)):
                income_ranges[key] = count
                total_households += count
        
        if total_households == 0:
            return {
                'planning_area': income_data.get('planningArea', ''),
                'total_households': 0,
                'weighted_average_income': 0.0,
                'income_distribution': {}
            }
        
        # Calculate weighted average
        for income_range, count in income_ranges.items():
            midpoint = self.calculate_income_midpoint(income_range)
            weighted_sum += midpoint * count
        
        weighted_average = weighted_sum / total_households
        
        return {
            'planning_area': income_data.get('planning_area', ''),
            'total_households': total_households,
            'weighted_average_income': weighted_average,
            'income_distribution': income_ranges
        }
    
    def get_all_planning_area_names(self) -> List[str]:
        """
        Get list of all planning area names from OneMap
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
    
    def process_all_income_data(self, year: str = "2020") -> pd.DataFrame:
        """
        Process household income data for all planning areas
        """
        print(f"Fetching household income data for year {year}...")
        
        # Get all planning area names
        planning_areas = self.get_all_planning_area_names()
        
        if not planning_areas:
            print("No planning areas found!")
            return pd.DataFrame()
        
        print(f"Found {len(planning_areas)} planning areas to process")
        
        all_income_data = []
        
        for i, area in enumerate(planning_areas, 1):
            print(f"Processing {i}/{len(planning_areas)}: {area}")
            
            # Get income data for this planning area
            income_data = self.get_household_income_data(area, year)
            
            if income_data:
                # Calculate weighted average
                processed_data = self.calculate_weighted_average_income(income_data)
                all_income_data.append(processed_data)
            
            # Rate limiting
            time.sleep(0.5)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_income_data)
        
        if not df.empty:
            # Sort by weighted average income
            df = df.sort_values('weighted_average_income', ascending=False)
            
            print(f"Processed income data for {len(df)} planning areas")
        
        return df
    
    def save_to_csv(self, df: pd.DataFrame, filepath: str):
        """
        Save DataFrame to CSV file
        """
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        df.to_csv(filepath, index=False)
        print(f"Saved {len(df)} income records to {filepath}")

def main():
    """
    Main function to extract household income data from OneMap
    """
    print("Starting OneMap household income data extraction...")
    
    # Initialize extractor
    extractor = OneMapIncomeDataExtractor()
    
    # Process all income data
    df = extractor.process_all_income_data()
    
    if not df.empty:
        # Save to CSV
        extractor.save_to_csv(df, INCOME_DATA_OUTPUT)
        
        # Print summary
        print("\nExtraction Summary:")
        print(f"Total planning areas with income data: {len(df)}")
        print(f"Average weighted income across all areas: ${df['weighted_average_income'].mean():.2f}")
        print(f"Highest average income: {df.iloc[0]['planning_area']} (${df.iloc[0]['weighted_average_income']:.2f})")
        print(f"Lowest average income: {df.iloc[-1]['planning_area']} (${df.iloc[-1]['weighted_average_income']:.2f})")
        
        print("\nTop 10 areas by average income:")
        for i, row in df.head(10).iterrows():
            print(f"{row['planning_area']}: ${row['weighted_average_income']:.2f}")
    
    return df

if __name__ == "__main__":
    main()
