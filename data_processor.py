import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any
import os
from config import GOOGLE_MAPS_OUTPUT, PLANNING_AREAS_OUTPUT, INCOME_DATA_OUTPUT, COMBINED_DATA_OUTPUT

class DataProcessor:
    def __init__(self):
        self.fitness_categories = {
            'BFT': ['bft', 'bodyfit', 'body fit'],
            'Fitness Studio': ['fitness', 'studio', 'training', 'hiit', 'circuit', 'functional'],
            'Yoga/Pilates Studio': ['yoga', 'pilates', 'reformer', 'megaformer', 'lagree', 'bikram', 'yin', 'aerial'],
            'Gym': ['gym', 'fitness center', 'fitness centre', 'weightlifting', 'powerlifting', 'calisthenics'],
            'Martial Arts': ['boxing', 'kickboxing', 'muay thai', 'mma', 'bjj', 'judo', 'taekwondo', 'karate', 'krav maga', 'silat'],
            'Dance Studio': ['dance', 'zumba', 'barre', 'pole', 'aerial arts'],
            'Cycling/Spin': ['spin', 'cycling', 'rhythm cycling', 'indoor cycling'],
            'Others': []  # Catch-all for anything not categorized
        }
    
    def categorize_fitness_location(self, name: str, search_query: str) -> str:
        """
        Categorize a fitness location based on its name and search query
        """
        name_lower = name.lower()
        query_lower = search_query.lower()
        
        # Check each category
        for category, keywords in self.fitness_categories.items():
            for keyword in keywords:
                if keyword in name_lower or keyword in query_lower:
                    return category
        
        # If no specific category found, return 'Others'
        return 'Others'
    
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all data files
        """
        data = {}
        
        # Load fitness locations
        if os.path.exists(GOOGLE_MAPS_OUTPUT):
            data['fitness_locations'] = pd.read_csv(GOOGLE_MAPS_OUTPUT)
            print(f"Loaded {len(data['fitness_locations'])} fitness locations")
        else:
            print("Fitness locations file not found!")
            data['fitness_locations'] = pd.DataFrame()
        
        # Load planning areas
        if os.path.exists(PLANNING_AREAS_OUTPUT):
            data['planning_areas'] = pd.read_csv(PLANNING_AREAS_OUTPUT)
            print(f"Loaded {len(data['planning_areas'])} planning areas")
        else:
            print("Planning areas file not found!")
            data['planning_areas'] = pd.DataFrame()
        
        # Load income data
        if os.path.exists(INCOME_DATA_OUTPUT):
            data['income_data'] = pd.read_csv(INCOME_DATA_OUTPUT)
            print(f"Loaded {len(data['income_data'])} income records")
        else:
            print("Income data file not found!")
            data['income_data'] = pd.DataFrame()
        
        return data
    
    def assign_planning_areas(self, fitness_df: pd.DataFrame, planning_areas_df: pd.DataFrame) -> pd.DataFrame:
        """
        Assign planning areas to fitness locations based on coordinates
        """
        if fitness_df.empty or planning_areas_df.empty:
            return fitness_df
        
        # Create a copy to avoid modifying original
        df = fitness_df.copy()
        df['planning_area'] = 'Unknown'
        
        # For each fitness location, find the planning area it's in
        for idx, location in df.iterrows():
            lat = location['latitude']
            lng = location['longitude']
            
            # Simple distance-based assignment (nearest centroid)
            min_distance = float('inf')
            nearest_area = 'Unknown'
            
            for _, area in planning_areas_df.iterrows():
                area_lat = area['centroid_latitude']
                area_lng = area['centroid_longitude']
                
                # Calculate simple Euclidean distance
                distance = np.sqrt((lat - area_lat)**2 + (lng - area_lng)**2)
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_area = area['planning_area_name']
            
            df.at[idx, 'planning_area'] = nearest_area
        
        return df
    
    def merge_income_data(self, fitness_df: pd.DataFrame, income_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge income data with fitness locations
        """
        if fitness_df.empty:
            return fitness_df
        
        if income_df.empty:
            # Add default income columns if no income data available
            fitness_df['weighted_average_income'] = 0
            fitness_df['total_households'] = 0
            return fitness_df
        
        # Normalize planning area names for matching
        fitness_df['planning_area_normalized'] = fitness_df['planning_area'].str.upper()
        income_df['planning_area_normalized'] = income_df['planning_area'].str.upper()
        
        # Merge on normalized planning area
        merged_df = fitness_df.merge(
            income_df[['planning_area_normalized', 'weighted_average_income', 'total_households']],
            left_on='planning_area_normalized',
            right_on='planning_area_normalized',
            how='left'
        )
        
        # Clean up temporary column
        merged_df = merged_df.drop(columns=['planning_area_normalized'])
        
        return merged_df
    
    def process_and_combine_data(self) -> pd.DataFrame:
        """
        Main function to process and combine all data
        """
        print("Loading and processing data...")
        
        # Load all data
        data = self.load_data()
        
        if data['fitness_locations'].empty:
            print("No fitness locations data available!")
            return pd.DataFrame()
        
        # Categorize fitness locations
        print("Categorizing fitness locations...")
        data['fitness_locations']['category'] = data['fitness_locations'].apply(
            lambda row: self.categorize_fitness_location(row['name'], row['search_query']),
            axis=1
        )
        
        # Assign planning areas
        if not data['planning_areas'].empty:
            print("Assigning planning areas...")
            data['fitness_locations'] = self.assign_planning_areas(
                data['fitness_locations'], 
                data['planning_areas']
            )
        
        # Merge income data
        if not data['income_data'].empty:
            print("Merging income data...")
            data['fitness_locations'] = self.merge_income_data(
                data['fitness_locations'],
                data['income_data']
            )
        
        # Final processing
        final_df = data['fitness_locations'].copy()
        
        # Fill missing values
        if 'weighted_average_income' in final_df.columns:
            final_df['weighted_average_income'] = final_df['weighted_average_income'].fillna(0)
        else:
            final_df['weighted_average_income'] = 0
            
        if 'total_households' in final_df.columns:
            final_df['total_households'] = final_df['total_households'].fillna(0)
        else:
            final_df['total_households'] = 0
            
        if 'planning_area' in final_df.columns:
            final_df['planning_area'] = final_df['planning_area'].fillna('Unknown')
        else:
            final_df['planning_area'] = 'Unknown'
        
        # Add some derived columns
        final_df['has_website'] = final_df['website'].notna() & (final_df['website'] != '')
        final_df['has_phone'] = final_df['phone_number'].notna() & (final_df['phone_number'] != '')
        final_df['has_rating'] = final_df['rating'] > 0
        
        # Add search coverage analysis
        final_df['search_coverage'] = final_df['search_location'].apply(lambda x: 'Local' if x != 'Singapore' else 'General')
        
        print(f"Final dataset has {len(final_df)} fitness locations")
        return final_df
    
    def save_combined_data(self, df: pd.DataFrame):
        """
        Save combined data to CSV
        """
        if df.empty:
            print("No data to save!")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(COMBINED_DATA_OUTPUT), exist_ok=True)
        
        df.to_csv(COMBINED_DATA_OUTPUT, index=False)
        print(f"Saved combined data to {COMBINED_DATA_OUTPUT}")
    
    def generate_summary_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate summary statistics for the combined dataset
        """
        if df.empty:
            return {}
        
        summary = {
            'total_locations': len(df),
            'categories': df['category'].value_counts().to_dict(),
            'planning_areas': df['planning_area'].value_counts().to_dict(),
            'average_rating': df['rating'].mean(),
            'locations_with_websites': df['has_website'].sum(),
            'locations_with_phones': df['has_phone'].sum(),
            'locations_with_ratings': df['has_rating'].sum(),
            'search_coverage': df['search_coverage'].value_counts().to_dict(),
            'unique_search_locations': df['search_location'].nunique(),
            'average_income_by_category': df.groupby('category')['weighted_average_income'].mean().to_dict(),
            'top_rated_locations': df.nlargest(10, 'rating')[['name', 'category', 'rating', 'planning_area']].to_dict('records'),
            'income_statistics': {
                'mean': df['weighted_average_income'].mean(),
                'median': df['weighted_average_income'].median(),
                'min': df['weighted_average_income'].min(),
                'max': df['weighted_average_income'].max()
            }
        }
        
        return summary

def main():
    """
    Main function to process and combine all data
    """
    print("Starting data processing and combination...")
    
    # Initialize processor
    processor = DataProcessor()
    
    # Process and combine data
    combined_df = processor.process_and_combine_data()
    
    if not combined_df.empty:
        # Save combined data
        processor.save_combined_data(combined_df)
        
        # Generate and print summary statistics
        summary = processor.generate_summary_statistics(combined_df)
        
        print("\n" + "="*50)
        print("SUMMARY STATISTICS")
        print("="*50)
        print(f"Total fitness locations: {summary['total_locations']}")
        print(f"Average rating: {summary['average_rating']:.2f}")
        print(f"Locations with websites: {summary['locations_with_websites']}")
        print(f"Locations with phone numbers: {summary['locations_with_phones']}")
        print(f"Search coverage: {summary['search_coverage']}")
        print(f"Unique search locations used: {summary['unique_search_locations']}")
        
        print("\nCategories:")
        for category, count in summary['categories'].items():
            print(f"  {category}: {count}")
        
        print("\nAverage income by category:")
        for category, income in summary['average_income_by_category'].items():
            print(f"  {category}: ${income:.2f}")
        
        print("\nTop 10 rated locations:")
        for i, location in enumerate(summary['top_rated_locations'][:10], 1):
            print(f"  {i}. {location['name']} ({location['category']}) - {location['rating']:.1f} stars in {location['planning_area']}")
    
    return combined_df

if __name__ == "__main__":
    main()
