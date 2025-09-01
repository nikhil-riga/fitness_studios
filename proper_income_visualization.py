import folium
import pandas as pd
import json
import os

def create_proper_income_visualization():
    """
    Create income visualization using real planning area coordinates from OneMap
    """
    # Load data
    planning_areas_path = "data/planning_areas.csv"
    income_path = "data/household_income.csv"
    
    if not os.path.exists(planning_areas_path) or not os.path.exists(income_path):
        print("Planning areas or income data not found!")
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
    
    # Create base map
    singapore_center = [1.3521, 103.8198]
    map_obj = folium.Map(
        location=singapore_center,
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Filter to planning areas with income data
    income_df_filtered = merged_df[merged_df['weighted_average_income'].notna()].copy()
    
    if income_df_filtered.empty:
        print("No planning areas with income data found!")
        return None
    
    # Get income range for color scaling
    min_income = income_df_filtered['weighted_average_income'].min()
    max_income = income_df_filtered['weighted_average_income'].max()
    
    print(f"Income range: ${min_income:,.0f} - ${max_income:,.0f}")
    
    # Define 4 income levels with blue shades
    income_levels = {
        'High': {'min': 15000, 'max': 20000, 'color': '#0000ff', 'description': 'High Income (>$15,000)'},
        'Medium-High': {'min': 12000, 'max': 15000, 'color': '#6666ff', 'description': 'Medium-High Income ($12,000-$15,000)'},
        'Medium': {'min': 10000, 'max': 12000, 'color': '#9999ff', 'description': 'Medium Income ($10,000-$12,000)'},
        'Low': {'min': 8000, 'max': 10000, 'color': '#ccccff', 'description': 'Low Income (<$10,000)'}
    }
    
    # Create polygons for each planning area
    for idx, row in income_df_filtered.iterrows():
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
            
            income = row['weighted_average_income']
            
            # Determine income level and color
            if income >= 15000:
                level = 'High'
            elif income >= 12000:
                level = 'Medium-High'
            elif income >= 10000:
                level = 'Medium'
            else:
                level = 'Low'
            
            color = income_levels[level]['color']
            
            # Create polygon
            polygon = folium.Polygon(
                locations=coords,
                popup=f"<b>{row['planning_area_name']}</b><br>Income: <b>${income:,.0f}</b><br>{income_levels[level]['description']}",
                color='blue',
                fill=True,
                fillColor=color,
                fillOpacity=0.8,
                weight=2
            )
            
            polygon.add_to(map_obj)
            print(f"Added {row['planning_area_name']}: ${income:,.0f} ({level} - {color})")
            
        except Exception as e:
            print(f"Error processing {row.get('planning_area_name', 'Unknown')}: {e}")
            continue
    
    # Create legend
    legend_html = """
    <div style="position: fixed; 
                top: 10px; 
                left: 10px; 
                width: 280px; 
                height: auto; 
                background-color: white; 
                border: 2px solid grey; 
                z-index: 1000; 
                font-size: 12px;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0,0,0,0.3);">
        <h4>Singapore Household Income by Planning Area</h4>
        <p><strong>Income Levels:</strong></p>
        <div style="margin: 5px 0;">
            <div style="display: flex; align-items: center; margin: 2px 0;">
                <div style="width: 20px; height: 20px; background: #0000ff; margin-right: 10px;"></div>
                <span>High Income (>$15,000)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 2px 0;">
                <div style="width: 20px; height: 20px; background: #6666ff; margin-right: 10px;"></div>
                <span>Medium-High ($12,000-$15,000)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 2px 0;">
                <div style="width: 20px; height: 20px; background: #9999ff; margin-right: 10px;"></div>
                <span>Medium ($10,000-$12,000)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 2px 0;">
                <div style="width: 20px; height: 20px; background: #ccccff; margin-right: 10px;"></div>
                <span>Low Income (<$10,000)</span>
            </div>
        </div>
        <hr>
        <p><strong>Instructions:</strong></p>
        <ul style="font-size: 11px;">
            <li>Click on colored areas for details</li>
            <li>Zoom and pan to explore</li>
            <li>Dark blue = High income</li>
            <li>Light blue = Low income</li>
        </ul>
        <hr>
        <p><strong>Data Source:</strong></p>
        <p style="font-size: 10px;">OneMap Singapore Planning Areas & Household Income Data</p>
    </div>
    """
    
    map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    output_file = "proper_income_map.html"
    map_obj.save(output_file)
    print(f"\nProper income map saved to {output_file}")
    print("Open this file in your browser to view the income visualization")
    
    return output_file

if __name__ == "__main__":
    create_proper_income_visualization()

