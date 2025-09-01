import folium
import pandas as pd
import json

def create_simple_income_visualization():
    """
    Create a simple income visualization with manually defined planning areas
    """
    # Create base map
    singapore_center = [1.3521, 103.8198]
    map_obj = folium.Map(
        location=singapore_center,
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Define simple polygon coordinates for key planning areas
    # These are simplified rectangular areas for demonstration
    planning_areas_data = {
        'Tanglin': {
            'coords': [[1.30, 103.80], [1.30, 103.85], [1.35, 103.85], [1.35, 103.80], [1.30, 103.80]],
            'income': 16324,
            'description': 'High Income Area'
        },
        'Bukit Timah': {
            'coords': [[1.32, 103.78], [1.32, 103.82], [1.37, 103.82], [1.37, 103.78], [1.32, 103.78]],
            'income': 15710,
            'description': 'High Income Area'
        },
        'River Valley': {
            'coords': [[1.28, 103.83], [1.28, 103.87], [1.33, 103.87], [1.33, 103.83], [1.28, 103.83]],
            'income': 15695,
            'description': 'High Income Area'
        },
        'Downtown Core': {
            'coords': [[1.27, 103.84], [1.27, 103.86], [1.30, 103.86], [1.30, 103.84], [1.27, 103.84]],
            'income': 14926,
            'description': 'Medium-High Income Area'
        },
        'Marine Parade': {
            'coords': [[1.29, 103.90], [1.29, 103.95], [1.34, 103.95], [1.34, 103.90], [1.29, 103.90]],
            'income': 12828,
            'description': 'Medium Income Area'
        },
        'Bishan': {
            'coords': [[1.35, 103.85], [1.35, 103.88], [1.38, 103.88], [1.38, 103.85], [1.35, 103.85]],
            'income': 12483,
            'description': 'Medium Income Area'
        },
        'Bedok': {
            'coords': [[1.32, 103.92], [1.32, 103.97], [1.37, 103.97], [1.37, 103.92], [1.32, 103.92]],
            'income': 10711,
            'description': 'Medium-Low Income Area'
        },
        'Woodlands': {
            'coords': [[1.42, 103.75], [1.42, 103.80], [1.47, 103.80], [1.47, 103.75], [1.42, 103.75]],
            'income': 9184,
            'description': 'Low Income Area'
        },
        'Yishun': {
            'coords': [[1.40, 103.82], [1.40, 103.87], [1.45, 103.87], [1.45, 103.82], [1.40, 103.82]],
            'income': 9019,
            'description': 'Low Income Area'
        }
    }
    
    # Define 4 income levels with blue shades
    income_levels = {
        'High': {'min': 15000, 'max': 20000, 'color': '#0000ff', 'description': 'High Income (>$15,000)'},
        'Medium-High': {'min': 12000, 'max': 15000, 'color': '#6666ff', 'description': 'Medium-High Income ($12,000-$15,000)'},
        'Medium': {'min': 10000, 'max': 12000, 'color': '#9999ff', 'description': 'Medium Income ($10,000-$12,000)'},
        'Low': {'min': 8000, 'max': 10000, 'color': '#ccccff', 'description': 'Low Income (<$10,000)'}
    }
    
    # Create polygons for each planning area
    for area_name, area_data in planning_areas_data.items():
        income = area_data['income']
        
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
            locations=area_data['coords'],
            popup=f"<b>{area_name}</b><br>Income: <b>${income:,.0f}</b><br>{area_data['description']}",
            color='blue',
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            weight=2
        )
        
        polygon.add_to(map_obj)
        print(f"Added {area_name}: ${income:,.0f} ({level} - {color})")
    
    # Create legend
    legend_html = """
    <div style="position: fixed; 
                top: 10px; 
                left: 10px; 
                width: 250px; 
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
    </div>
    """
    
    map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the map
    output_file = "simple_income_map.html"
    map_obj.save(output_file)
    print(f"\nSimple income map saved to {output_file}")
    print("Open this file in your browser to view the income visualization")
    
    return output_file

if __name__ == "__main__":
    create_simple_income_visualization()

