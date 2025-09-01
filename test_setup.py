#!/usr/bin/env python3
"""
Test script to verify the setup and dependencies are working correctly.
"""

import sys
import importlib
import requests
from config import GOOGLE_MAPS_API_KEY, ONEMAP_BASE_URL, ONEMAP_ACCESS_TOKEN

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    required_modules = [
        'pandas',
        'folium',
        'requests',
        'numpy',
        'json',
        'os',
        'time'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All modules imported successfully!")
    return True

def test_google_maps_api():
    """Test Google Maps API connectivity"""
    print("\n🔍 Testing Google Maps API...")
    
    try:
        # Test with a simple search
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': 'gym in Singapore',
            'key': GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('status') == 'OK':
            print(f"  ✅ API working - Found {len(data.get('results', []))} results")
            return True
        else:
            print(f"  ❌ API Error: {data.get('status')}")
            if data.get('status') == 'REQUEST_DENIED':
                print("  💡 Check your API key and ensure Places API is enabled")
            return False
            
    except Exception as e:
        print(f"  ❌ Connection error: {e}")
        return False

def test_onemap_api():
    """Test OneMap API connectivity"""
    print("\n🔍 Testing OneMap API...")
    
    try:
        # Test planning areas endpoint
        url = f"{ONEMAP_BASE_URL}/getPlanningareaNames"
        params = {'year': '2019'}
        headers = {'Authorization': f'Bearer {ONEMAP_ACCESS_TOKEN}'}
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if 'SearchResults' in data:
            areas = data.get('SearchResults', [])
            print(f"  ✅ API working - Found {len(areas)} planning areas")
            return True
        else:
            print(f"  ❌ API Error: Unexpected response format")
            return False
            
    except Exception as e:
        print(f"  ❌ Connection error: {e}")
        return False

def test_config():
    """Test configuration file"""
    print("\n🔍 Testing configuration...")
    
    try:
        from config import (
            GOOGLE_MAPS_API_KEY, 
            ONEMAP_BASE_URL, 
            FITNESS_KEYWORDS, 
            SINGAPORE_BOUNDS
        )
        
        print(f"  ✅ Google Maps API Key: {'*' * 10}{GOOGLE_MAPS_API_KEY[-4:]}")
        print(f"  ✅ OneMap Base URL: {ONEMAP_BASE_URL}")
        print(f"  ✅ Fitness Keywords: {len(FITNESS_KEYWORDS)} keywords")
        print(f"  ✅ Singapore Bounds: {SINGAPORE_BOUNDS}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration error: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'main.py',
        'config.py',
        'google_maps_extractor.py',
        'onemap_planning_areas.py',
        'onemap_income_data.py',
        'data_processor.py',
        'visualization.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    
    for file in required_files:
        try:
            with open(file, 'r') as f:
                print(f"  ✅ {file}")
        except FileNotFoundError:
            print(f"  ❌ {file} (missing)")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present!")
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 SINGAPORE FITNESS MAPPING - SETUP TEST")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Configuration", test_config),
        ("Module Imports", test_imports),
        ("OneMap API", test_onemap_api),
        ("Google Maps API", test_google_maps_api)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to run the main project.")
        print("Run: python main.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
