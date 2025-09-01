import folium
from folium import plugins
import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any
import os
from config import COMBINED_DATA_OUTPUT

class FitnessMapVisualizer:
    def __init__(self):
        # Singapore center coordinates
        self.singapore_center = [1.3521, 103.8198]
        
        # Color scheme for different categories
        self.category_colors = {
            'BFT': '#FF6B6B',  # Red
            'Fitness Studio': '#4ECDC4',  # Teal
            'Yoga/Pilates Studio': '#2E86AB',  # Darker Blue
            'Gym': '#9B59B6',  # Purple (changed from green)
            'Martial Arts': '#FFEAA7',  # Yellow
            'Others': '#F7DC6F',  # Light Yellow
            'ActiveSG': '#FF8C42'  # Orange
        }
        
        # Icon mapping for different categories
        self.category_icons = {
            'BFT': 'fire',
            'Fitness Studio': 'dumbbell',
            'Yoga/Pilates Studio': 'pray',
            'Gym': 'weight-hanging',
            'Martial Arts': 'fist-raised',
            'Others': 'map-marker',
            'ActiveSG': 'building'
        }
        
        # Income color scheme (green to red)
        self.income_colors = {
            'low': '#FF6B6B',      # Red for low income
            'medium': '#FFA500',   # Orange for medium income
            'high': '#4ECDC4'      # Green for high income
        }
    
    def load_data(self) -> pd.DataFrame:
        """
        Load the manually edited final fitness data
        """
        final_data_path = "data/final_fitness_locations.csv"
        if os.path.exists(final_data_path):
            df = pd.read_csv(final_data_path)
            print(f"Loaded {len(df)} manually edited fitness locations for visualization")
        else:
            print(f"Final data file not found: {final_data_path}")
            return pd.DataFrame()
        return df
    
    def load_planning_areas_and_income(self):
        """
        Load planning area polygons and income data
        """
        try:
            # Load planning areas data
            planning_areas_path = "data/planning_areas.csv"
            income_path = "data/household_income.csv"
            
            if not os.path.exists(planning_areas_path) or not os.path.exists(income_path):
                print("Planning areas or income data not found. Skipping polygon overlay.")
                return None, None
            
            planning_areas_df = pd.read_csv(planning_areas_path)
            income_df = pd.read_csv(income_path)
            
            # Normalize planning area names for merging (convert to title case)
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
            
            return merged_df, income_df
            
        except Exception as e:
            print(f"Error loading planning areas data: {e}")
            return None, None
    
    def create_base_map(self) -> folium.Map:
        """
        Create the base map centered on Singapore
        """
        return folium.Map(
            location=self.singapore_center,
            zoom_start=11,
            tiles='CartoDB positron'  # Clean black and white map
        )
    
    def add_fitness_locations(self, map_obj: folium.Map, df: pd.DataFrame) -> folium.Map:
        """
        Add fitness locations as markers to the map
        """
        if df.empty:
            return map_obj
        
        # Create feature groups for each category
        category_groups = {}
        for category in df['category'].unique():
            if category in self.category_colors:
                color = self.category_colors[category]
            else:
                color = self.category_colors['Others']
            
            category_groups[category] = folium.FeatureGroup(
                name=f"{category} ({len(df[df['category'] == category])})",
                overlay=True
            )
        
        # Add markers for each location
        for idx, row in df.iterrows():
            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                continue
            
            # Determine marker color based on category
            category = row['category']
            if category in self.category_colors:
                color = self.category_colors[category]
            else:
                color = self.category_colors['Others']
            
            # Create popup content
            popup_content = f"""
            <div style="width: 250px;">
                <h4>{row['name']}</h4>
                <p><strong>Category:</strong> {category}</p>
                <p><strong>Address:</strong> {row['formatted_address']}</p>
                <p><strong>Planning Area:</strong> {row['planning_area']}</p>
                <p><strong>Rating:</strong> {row['rating']:.1f} ⭐ ({row['user_ratings_total']} reviews)</p>
                <p><strong>Avg Income:</strong> ${row['weighted_average_income']:.0f}</p>
            """
            
            if row['website'] and pd.notna(row['website']):
                popup_content += f'<p><strong>Website:</strong> <a href="{row["website"]}" target="_blank">Visit</a></p>'
            
            if row['phone_number'] and pd.notna(row['phone_number']):
                popup_content += f'<p><strong>Phone:</strong> {row["phone_number"]}</p>'
            
            popup_content += "</div>"
            
            # Create custom pin marker with colored ball
            # Make BFT pins 50% larger
            if category == 'BFT':
                ball_size = 28  # 50% larger than 19px
                pin_height = 48  # 50% larger than 32px
                needle_top = 25  # Adjusted for larger ball
                icon_size = (45, 48)  # 50% larger than (30, 32)
                icon_anchor = (22, 48)  # Adjusted anchor
            else:
                ball_size = 19
                pin_height = 32
                needle_top = 17
                icon_size = (30, 32)
                icon_anchor = (15, 32)
            
            custom_icon_html = f"""
            <div style="position: relative; width: {icon_size[0]}px; height: {pin_height}px;">
                <!-- Colored ball on top -->
                <div style="position: absolute; top: 0; left: 50%; transform: translateX(-50%); 
                            width: {ball_size}px; height: {ball_size}px; background-color: {color}; 
                            border-radius: 50%; border: 1px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                </div>
                <!-- Needle/pin body -->
                <div style="position: absolute; top: {needle_top}px; left: 50%; transform: translateX(-50%); 
                            width: 2px; height: 15px; background-color: #333; 
                            border-radius: 1px;">
                </div>
            </div>
            """
            
            # Create custom icon
            custom_icon = folium.DivIcon(
                html=custom_icon_html,
                icon_size=icon_size,
                icon_anchor=icon_anchor  # Anchor at bottom center of pin
            )
            
            # Create marker with custom icon
            marker = folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                icon=custom_icon
            )
            
            # Add to appropriate category group
            if category in category_groups:
                marker.add_to(category_groups[category])
            else:
                marker.add_to(category_groups['Others'])
        
        # Add all category groups to the map
        for group in category_groups.values():
            group.add_to(map_obj)
        
        return map_obj
    
    def add_planning_area_income_overlay(self, map_obj: folium.Map) -> folium.Map:
        """
        Add planning area polygons with income data as overlay
        """
        planning_areas_df, income_df = self.load_planning_areas_and_income()
        
        if planning_areas_df is None or planning_areas_df.empty:
            print("No planning areas data available")
            return map_obj
        
        print(f"Loaded {len(planning_areas_df)} planning areas")
        print(f"Planning areas with income data: {planning_areas_df['weighted_average_income'].notna().sum()}")
        print(f"Available columns: {planning_areas_df.columns.tolist()}")
        
        try:
            # Create a feature group for planning areas
            planning_areas_group = folium.FeatureGroup(
                name='Planning Areas - Household Income',
                overlay=True,
                control=True
            )
            
            # Get income range for color scaling
            income_values = planning_areas_df['weighted_average_income'].dropna()
            if income_values.empty:
                return map_obj
            
            min_income = income_values.min()
            max_income = income_values.max()
            
            for idx, row in planning_areas_df.iterrows():
                if pd.isna(row['weighted_average_income']) or pd.isna(row['polygon_coordinates']):
                    continue
                
                try:
                    # Parse polygon coordinates
                    import json
                    coords_str = row['polygon_coordinates']
                    if isinstance(coords_str, str):
                        coords = json.loads(coords_str)
                    else:
                        coords = coords_str
                    
                    if not coords:
                        print(f"No coordinates for {row['planning_area_name']}")
                        continue
                    
                    print(f"Processing polygon for {row['planning_area_name']} with {len(coords)} coordinates")
                    
                    # Calculate color based on income with better color scheme
                    income = row['weighted_average_income']
                    if max_income > min_income:
                        normalized_income = (income - min_income) / (max_income - min_income)
                    else:
                        normalized_income = 0.5
                    
                    # Color gradient from blue (low) to red (high) - more intuitive
                    if normalized_income < 0.5:
                        # Blue to cyan for lower half
                        red = int(0)
                        green = int(255 * (normalized_income * 2))
                        blue = int(255)
                    else:
                        # Cyan to red for upper half
                        red = int(255 * ((normalized_income - 0.5) * 2))
                        green = int(255 * (1 - (normalized_income - 0.5) * 2))
                        blue = int(255 * (1 - (normalized_income - 0.5) * 2))
                    
                    color = f'#{red:02x}{green:02x}{blue:02x}'
                    
                    # Create polygon
                    polygon = folium.Polygon(
                        locations=coords,
                        popup=f"<b>{row['planning_area_name']}</b><br>Avg Income: ${income:,.0f}",
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.7,  # Even higher opacity for testing
                        weight=3  # Thicker border for testing
                    )
                    # Add polygon to feature group only
                    polygon.add_to(planning_areas_group)
                    print(f"Added polygon for {row['planning_area_name']} with color {color} and income ${income:,.0f}")
                    
                except Exception as e:
                    print(f"Error processing polygon for {row.get('planning_area_name', 'Unknown')}: {e}")
                    continue
            
            planning_areas_group.add_to(map_obj)
            print(f"Added planning areas feature group with {len(planning_areas_group._children)} polygons to map")
            
        except Exception as e:
            print(f"Error creating planning areas overlay: {e}")
        
        return map_obj
    
    def add_planning_area_boundaries(self, map_obj: folium.Map, df: pd.DataFrame) -> folium.Map:
        """
        Add planning area boundaries if polygon data is available
        """
        # This would require the polygon coordinates from the planning areas data
        # For now, we'll skip this as it requires more complex GeoJSON handling
        return map_obj
    
    def create_statistics_panel(self, df: pd.DataFrame) -> str:
        """
        Create HTML statistics panel
        """
        if df.empty:
            return ""
        
        stats_html = """
        <div style="position: fixed; 
                    top: 10px; 
                    left: 10px; 
                    width: 200px; 
                    height: auto; 
                    background-color: white; 
                    border:2px solid grey; 
                    z-index:9999; 
                    font-size:12px;
                    padding: 8px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.3);">
        <h3>Singapore Fitness Studios</h3>
        """
        
        # Basic statistics
        total_locations = len(df)
        avg_rating = df['rating'].mean()
        categories = df['category'].value_counts()
        
        stats_html += f"<p><strong>Total Locations:</strong> {total_locations}</p>"
        stats_html += f"<p><strong>Average Rating:</strong> {avg_rating:.1f} ⭐</p>"
        
        # Category breakdown
        stats_html += "<p><strong>Categories:</strong></p><ul>"
        for category, count in categories.items():
            percentage = (count / total_locations) * 100
            stats_html += f"<li>{category}: {count} ({percentage:.1f}%)</li>"
        stats_html += "</ul>"
        
        # Add legend with actual categories from data
        stats_html += """
        <hr style="margin: 8px 0;">
        <h4 style="margin: 5px 0;">Legend & Filters:</h4>
        <div style="font-size: 11px;">
        <p><strong>Pin Markers:</strong></p>
        <ul style="list-style: none; padding-left: 0;">
        """
        
        # Get actual categories from data and their colors
        category_counts = df['category'].value_counts()
        for category in category_counts.index:
            color = self.category_colors.get(category, '#F7DC6F')  # Default to light yellow if not found
            stats_html += f'<li><span style="color: {color}; font-size: 24px;">●</span> {category} ({category_counts[category]} locations)</li>'
        
        stats_html += """
        </ul>
        <p><strong>Filters:</strong></p>
        <p>Use the layer control (top-right) to:</p>
        <ul style="font-size: 11px;">
            <li>Show/hide specific categories</li>
            <li>All layers are visible by default</li>
        </ul>
        <p><strong>Instructions:</strong></p>
        <ul style="font-size: 11px;">
            <li>Click markers for details</li>
            <li>Use layer control to filter categories</li>
            <li>Zoom and pan to explore areas</li>
        </ul>
        </div>
        """
        
        stats_html += "</div>"
        
        return stats_html
    
    def create_visualization(self, output_file: str = "singapore_fitness_map.html") -> str:
        """
        Create the complete visualization
        """
        print("Creating Singapore fitness map visualization...")
        
        # Load data
        df = self.load_data()
        
        if df.empty:
            print("No data available for visualization!")
            return ""
        
        # Create base map
        map_obj = self.create_base_map()
        
        # Add fitness locations
        map_obj = self.add_fitness_locations(map_obj, df)
        
        # Add layer control - this must be added after all layers
        folium.LayerControl(
            position='topright',
            collapsed=False,
            overlay=True
        ).add_to(map_obj)
        
        # Create statistics panel
        stats_panel = self.create_statistics_panel(df)
        
        # Save the map
        map_obj.save(output_file)
        
        # Add statistics panel to the HTML file
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Insert statistics panel before closing body tag
        if stats_panel:
            html_content = html_content.replace('</body>', f'{stats_panel}\n</body>')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Map saved to {output_file}")
        return output_file
    
    def create_category_analysis_chart(self, df: pd.DataFrame) -> str:
        """
        Create a separate HTML file with category analysis charts
        """
        if df.empty:
            return ""
        
        # Create category analysis
        category_stats = df.groupby('category').agg({
            'rating': ['mean', 'count'],
            'weighted_average_income': 'mean',
            'user_ratings_total': 'sum'
        }).round(2)
        
        # Flatten column names
        category_stats.columns = ['avg_rating', 'count', 'avg_income', 'total_reviews']
        category_stats = category_stats.reset_index()
        
        # Create HTML report
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Singapore Fitness Studios Analysis</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .highlight { background-color: #e6f3ff; }
            </style>
        </head>
        <body>
            <h1>Singapore Fitness Studios Analysis</h1>
        """
        
        # Summary statistics
        html_content += f"""
        <h2>Summary Statistics</h2>
        <p><strong>Total Locations:</strong> {len(df)}</p>
        <p><strong>Average Rating:</strong> {df['rating'].mean():.2f} ⭐</p>
        <p><strong>Average Household Income:</strong> ${df['weighted_average_income'].mean():.0f}</p>
        """
        
        # Category breakdown table
        html_content += """
        <h2>Category Breakdown</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Count</th>
                <th>Percentage</th>
                <th>Avg Rating</th>
                <th>Avg Income</th>
                <th>Total Reviews</th>
            </tr>
        """
        
        for _, row in category_stats.iterrows():
            percentage = (row['count'] / len(df)) * 100
            html_content += f"""
            <tr>
                <td>{row['category']}</td>
                <td>{row['count']}</td>
                <td>{percentage:.1f}%</td>
                <td>{row['avg_rating']:.1f} ⭐</td>
                <td>${row['avg_income']:.0f}</td>
                <td>{row['total_reviews']}</td>
            </tr>
            """
        
        html_content += "</table>"
        
        # Top rated locations
        top_rated = df.nlargest(10, 'rating')[['name', 'category', 'rating', 'planning_area', 'weighted_average_income']]
        
        html_content += """
        <h2>Top 10 Rated Locations</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Name</th>
                <th>Category</th>
                <th>Rating</th>
                <th>Planning Area</th>
                <th>Avg Income</th>
            </tr>
        """
        
        for i, (_, row) in enumerate(top_rated.iterrows(), 1):
            html_content += f"""
            <tr class="highlight">
                <td>{i}</td>
                <td>{row['name']}</td>
                <td>{row['category']}</td>
                <td>{row['rating']:.1f} ⭐</td>
                <td>{row['planning_area']}</td>
                <td>${row['weighted_average_income']:.0f}</td>
            </tr>
            """
        
        html_content += "</table></body></html>"
        
        # Save analysis file
        analysis_file = "fitness_analysis_report.html"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Analysis report saved to {analysis_file}")
        return analysis_file



def main():
    """
    Main function to create the visualization
    """
    print("Starting visualization creation...")
    
    # Initialize visualizer
    visualizer = FitnessMapVisualizer()
    
    # Create the main map
    map_file = visualizer.create_visualization()
    
    # Load data for analysis
    df = visualizer.load_data()
    
    if not df.empty:
        # Create analysis report
        analysis_file = visualizer.create_category_analysis_chart(df)
        
        print(f"\nVisualization complete!")
        print(f"Interactive map: {map_file}")
        print(f"Analysis report: {analysis_file}")
    
    return map_file

if __name__ == "__main__":
    main()
