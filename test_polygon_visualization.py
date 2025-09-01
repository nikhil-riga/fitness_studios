import folium
import json

def test_polygon_visualization():
    """
    Test basic polygon visualization with simple test data
    """
    # Create a simple map centered on Singapore
    singapore_center = [1.3521, 103.8198]
    map_obj = folium.Map(
        location=singapore_center,
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Create a simple test polygon (rectangle around Singapore center)
    test_polygon_coords = [
        [1.3, 103.7],  # Southwest
        [1.3, 103.9],  # Southeast  
        [1.4, 103.9],  # Northeast
        [1.4, 103.7],  # Northwest
        [1.3, 103.7]   # Close the polygon
    ]
    
    # Create polygon with blue color
    test_polygon = folium.Polygon(
        locations=test_polygon_coords,
        popup="Test Polygon - If you see this blue area, polygons work!",
        color='blue',
        fill=True,
        fillColor='blue',
        fillOpacity=0.8,
        weight=3
    )
    
    # Add polygon to map
    test_polygon.add_to(map_obj)
    
    # Add a legend
    legend_html = """
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
        <h4>Test Polygon Visualization</h4>
        <p><strong>Instructions:</strong></p>
        <ul style="font-size: 11px;">
            <li>You should see a blue rectangle on the map</li>
            <li>Click on the blue area for a popup</li>
            <li>If you can see this, polygon visualization works!</li>
        </ul>
    </div>
    """
    
    map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    # Save the test map
    output_file = "test_polygon_map.html"
    map_obj.save(output_file)
    print(f"Test polygon map saved to {output_file}")
    print("Open this file in your browser to test polygon visualization")
    
    return output_file

if __name__ == "__main__":
    test_polygon_visualization()

