import folium
import pandas as pd
import os
import json

class IncomeVisualizer:
    def __init__(self):
        self.singapore_center = [1.3521, 103.8198]
    
    def load_data(self):
        """
        Load planning areas and income data
        """
        try:
            # Load planning areas data
            planning_areas_path = "data/planning_areas.csv"
            income_path = "data/household_income.csv"
            
            if not os.path.exists(planning_areas_path) or not os.path.exists(income_path):
                print("Planning areas or income data not found.")
                return None
            
            planning_areas_df = pd.read_csv(planning_areas_path)
            income_df = pd.read_csv(income_path)
            
            print(f"Loaded {len(planning_areas_df)} planning areas")
            print(f"Loaded {len(income_df)} income data entries")
            
            # Normalize planning area names for merging
            planning_areas_df['planning_area_normalized'] = planning_areas_df['planning_area_name'].str.title()
            income_df['planning_area_normalized'] = income_df['planning_area'].str.title()
            
            # Merge planning areas with income data
            merged_df = planning_areas_df.merge(
                income_df[['planning_area_normalized', 'weighted_average_income']], 
                left_on='planning_area_normalized', 
                right_on='planning_area_normalized', 
                how='left'
            )
            
            # Clean up temporary column
            merged_df = merged_df.drop(columns=['planning_area_normalized'])
            
            print(f"Merged data shape: {merged_df.shape}")
            print(f"Planning areas with income data: {merged_df['weighted_average_income'].notna().sum()}")
            
            return merged_df
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def create_income_map(self, df):
        """
        Create a map showing household income by planning area
        """
        if df is None or df.empty:
            print("No data available for visualization!")
            return None
        
        # Create base map with OpenStreetMap tiles
        map_obj = folium.Map(
            location=self.singapore_center,
            zoom_start=11,
            tiles='OpenStreetMap'  # Use OpenStreetMap instead
        )
        
        # Create a feature group for income polygons
        income_group = folium.FeatureGroup(name="Household Income", show=True)
        
        # Filter to planning areas with income data
        income_df = df[df['weighted_average_income'].notna()].copy()
        
        if income_df.empty:
            print("No planning areas with income data found!")
            return map_obj
        
        # Get income range for color scaling
        min_income = income_df['weighted_average_income'].min()
        max_income = income_df['weighted_average_income'].max()
        
        print(f"Income range: ${min_income:,.0f} - ${max_income:,.0f}")
        
        # Create polygons for each planning area using blue shades (dark to light)
        for idx, row in income_df.iterrows():
            try:
                # Parse polygon coordinates
                coords_str = row['polygon_coordinates']
                if isinstance(coords_str, str):
                    coords = json.loads(coords_str)
                else:
                    coords = coords_str
                
                if not coords:
                    print(f"No coordinates for {row['planning_area_name']}")
                    continue
                
                # Calculate blue shade based on income (dark blue = high income, light blue = low income)
                income = row['weighted_average_income']
                if max_income > min_income:
                    normalized_income = (income - min_income) / (max_income - min_income)
                else:
                    normalized_income = 0.5
                
                # Dark blue for high income, light blue for low income
                blue_intensity = int(255 * (1 - normalized_income))  # Darker for higher income
                blue_color = f'#{0:02x}{0:02x}{blue_intensity:02x}'  # Pure blue with varying intensity
                
                # Create polygon with blue shades
                polygon = folium.Polygon(
                    locations=coords,
                    popup=f"<b>{row['planning_area_name']}</b><br>Average Household Income: <b>${income:,.0f}</b>",
                    color='blue',
                    fill=True,
                    fillColor=blue_color,
                    fillOpacity=0.8,
                    weight=2
                )
                
                # Add polygon to the feature group
                polygon.add_to(income_group)
                
                print(f"Added {row['planning_area_name']}: ${income:,.0f} (blue intensity: {blue_intensity})")
                
            except Exception as e:
                print(f"Error processing {row.get('planning_area_name', 'Unknown')}: {e}")
                continue
        
        # Add the feature group to the map
        income_group.add_to(map_obj)
        
        # Add a legend
        legend_html = f"""
        <div style="position: fixed; 
                    top: 10px; 
                    left: 10px; 
                    width: 200px; 
                    height: auto; 
                    background-color: white; 
                    border: 2px solid grey; 
                    z-index: 1000; 
                    font-size: 12px;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.3);">
            <h4>Household Income by Planning Area</h4>
            <p><strong>Income Range:</strong></p>
            <p>${min_income:,.0f} - ${max_income:,.0f}</p>
            <hr>
            <p><strong>Color Legend:</strong></p>
            <div style="margin: 5px 0;">
                <div style="display: flex; align-items: center; margin: 2px 0;">
                    <div style="width: 15px; height: 15px; background: #0000ff; margin-right: 10px;"></div>
                    <span>Dark Blue: High Income</span>
                </div>
                <div style="display: flex; align-items: center; margin: 2px 0;">
                    <div style="width: 15px; height: 15px; background: #6666ff; margin-right: 10px;"></div>
                    <span>Medium Blue: Medium Income</span>
                </div>
                <div style="display: flex; align-items: center; margin: 2px 0;">
                    <div style="width: 15px; height: 15px; background: #ccccff; margin-right: 10px;"></div>
                    <span>Light Blue: Low Income</span>
                </div>
            </div>
            <hr>
            <p><strong>Instructions:</strong></p>
            <ul style="font-size: 11px;">
                <li>Click on colored areas for details</li>
                <li>Zoom and pan to explore</li>
            </ul>
        </div>
        """
        
        map_obj.get_root().html.add_child(folium.Element(legend_html))
        
        return map_obj
    
    def create_visualization(self, output_file="singapore_income_map.html"):
        """
        Create the complete income visualization
        """
        print("Creating Singapore household income visualization...")
        
        # Load data
        df = self.load_data()
        
        if df is None:
            print("Failed to load data!")
            return None
        
        # Create map
        map_obj = self.create_income_map(df)
        
        if map_obj is None:
            print("Failed to create map!")
            return None
        
        # Save map
        map_obj.save(output_file)
        print(f"Income map saved to {output_file}")
        
        return output_file

def main():
    """
    Main function to create the income visualization
    """
    visualizer = IncomeVisualizer()
    output_file = visualizer.create_visualization()
    
    if output_file:
        print(f"\nVisualization complete!")
        print(f"Open {output_file} in your browser to view the income map.")
    else:
        print("Failed to create visualization.")

if __name__ == "__main__":
    main()
