#!/usr/bin/env python3
"""
Main script for Singapore Fitness Studios Mapping Project

This script orchestrates the entire pipeline:
1. Extract fitness locations from Google Maps
2. Extract planning areas from OneMap
3. Extract household income data from OneMap
4. Process and combine all data
5. Create interactive visualization

Usage:
    python main.py [--skip-google] [--skip-onemap] [--skip-visualization]
"""

import argparse
import sys
import os
from datetime import datetime

# Import our modules
from google_maps_extractor import main as extract_google_maps
from onemap_planning_areas import main as extract_planning_areas
from onemap_income_data import main as extract_income_data
from data_processor import main as process_data
from visualization import main as create_visualization

def print_banner():
    """Print project banner"""
    print("=" * 60)
    print("🏋️  SINGAPORE FITNESS STUDIOS MAPPING PROJECT 🏋️")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def print_step_header(step_name: str, step_number: int, total_steps: int):
    """Print step header"""
    print(f"\n{'='*20} STEP {step_number}/{total_steps} {'='*20}")
    print(f"🔄 {step_name}")
    print("=" * 60)

def print_step_footer(step_name: str, success: bool):
    """Print step footer"""
    if success:
        print(f"✅ {step_name} completed successfully!")
    else:
        print(f"❌ {step_name} failed!")

def check_dependencies():
    """Check if required files exist"""
    required_files = [
        'config.py',
        'google_maps_extractor.py',
        'onemap_planning_areas.py',
        'onemap_income_data.py',
        'data_processor.py',
        'visualization.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Singapore Fitness Studios Mapping Project')
    parser.add_argument('--skip-google', action='store_true', 
                       help='Skip Google Maps extraction (use existing data)')
    parser.add_argument('--skip-onemap', action='store_true', 
                       help='Skip OneMap extraction (use existing data)')
    parser.add_argument('--skip-visualization', action='store_true', 
                       help='Skip visualization creation')
    parser.add_argument('--data-only', action='store_true', 
                       help='Only extract data, skip visualization')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Please ensure all required files are present.")
        sys.exit(1)
    
    total_steps = 5
    current_step = 0
    
    try:
        # Step 1: Extract Google Maps data
        if not args.skip_google:
            current_step += 1
            print_step_header("Google Maps Data Extraction", current_step, total_steps)
            
            success = False
            try:
                extract_google_maps()
                success = True
            except Exception as e:
                print(f"Error in Google Maps extraction: {e}")
            
            print_step_footer("Google Maps Data Extraction", success)
            if not success:
                print("⚠️  Continuing with existing data if available...")
        else:
            print("⏭️  Skipping Google Maps extraction (--skip-google)")
        
        # Step 2: Extract OneMap planning areas
        if not args.skip_onemap:
            current_step += 1
            print_step_header("OneMap Planning Areas Extraction", current_step, total_steps)
            
            success = False
            try:
                extract_planning_areas()
                success = True
            except Exception as e:
                print(f"Error in OneMap planning areas extraction: {e}")
            
            print_step_footer("OneMap Planning Areas Extraction", success)
            if not success:
                print("⚠️  Continuing with existing data if available...")
        else:
            print("⏭️  Skipping OneMap planning areas extraction (--skip-onemap)")
        
        # Step 3: Extract OneMap income data
        if not args.skip_onemap:
            current_step += 1
            print_step_header("OneMap Income Data Extraction", current_step, total_steps)
            
            success = False
            try:
                extract_income_data()
                success = True
            except Exception as e:
                print(f"Error in OneMap income data extraction: {e}")
            
            print_step_footer("OneMap Income Data Extraction", success)
            if not success:
                print("⚠️  Continuing with existing data if available...")
        else:
            print("⏭️  Skipping OneMap income data extraction (--skip-onemap)")
        
        # Step 4: Process and combine data
        current_step += 1
        print_step_header("Data Processing and Combination", current_step, total_steps)
        
        success = False
        try:
            process_data()
            success = True
        except Exception as e:
            print(f"Error in data processing: {e}")
        
        print_step_footer("Data Processing and Combination", success)
        if not success:
            print("❌ Cannot continue without processed data!")
            sys.exit(1)
        
        # Step 5: Create visualization
        if not args.skip_visualization and not args.data_only:
            current_step += 1
            print_step_header("Visualization Creation", current_step, total_steps)
            
            success = False
            try:
                create_visualization()
                success = True
            except Exception as e:
                print(f"Error in visualization creation: {e}")
            
            print_step_footer("Visualization Creation", success)
        else:
            print("⏭️  Skipping visualization creation")
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎉 PROJECT COMPLETED SUCCESSFULLY! 🎉")
        print("=" * 60)
        
        # Check output files
        output_files = [
            'data/fitness_locations.csv',
            'data/planning_areas.csv', 
            'data/household_income.csv',
            'data/combined_data.csv'
        ]
        
        if not args.data_only:
            output_files.extend([
                'singapore_fitness_map.html',
                'fitness_analysis_report.html'
            ])
        
        print("\n📁 Generated Files:")
        for file in output_files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                print(f"   ✅ {file} ({size:,} bytes)")
            else:
                print(f"   ❌ {file} (not found)")
        
        print(f"\n⏱️  Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not args.data_only:
            print("\n🌐 To view the interactive map:")
            print("   Open 'singapore_fitness_map.html' in your web browser")
            print("\n📊 To view the analysis report:")
            print("   Open 'fitness_analysis_report.html' in your web browser")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
