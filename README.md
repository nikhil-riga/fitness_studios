# 🏋️ Singapore Fitness Studios Mapping Project

A comprehensive data visualization project that maps all fitness studios, gyms, yoga studios, and other fitness-related businesses in Singapore, overlaid with household income data from OneMap Singapore.

## 📋 Project Overview

This project extracts data from multiple sources to create an interactive map visualization:

1. **Google Maps API**: Extracts fitness locations with detailed information
2. **OneMap Singapore API**: Gets planning areas and household income data
3. **Data Processing**: Categorizes and combines all data sources
4. **Visualization**: Creates interactive maps with income overlays

## 🎯 Features

- **Comprehensive Fitness Location Database**: Covers gyms, yoga studios, pilates, martial arts, dance studios, and more
- **Income Data Overlay**: Shows household income distribution across planning areas
- **Interactive Map**: Color-coded categories with detailed popups
- **Statistical Analysis**: Detailed reports and analytics
- **Multiple Data Sources**: Google Maps + OneMap Singapore integration

## 📁 Project Structure

```
Fitness Studios/
├── main.py                     # Main orchestration script
├── config.py                   # Configuration and API keys
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── google_maps_extractor.py    # Google Maps data extraction
├── onemap_planning_areas.py    # OneMap planning areas extraction
├── onemap_income_data.py       # OneMap household income extraction
├── data_processor.py           # Data processing and categorization
├── visualization.py            # Map visualization creation
└── data/                       # Output data directory
    ├── fitness_locations.csv   # Extracted fitness locations
    ├── planning_areas.csv      # Planning areas data
    ├── household_income.csv    # Income data
    └── combined_data.csv       # Final combined dataset
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Maps API key (with Places API enabled)
- Internet connection for API calls

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys**:
   - Your Google Maps API key is already configured in `config.py`
   - OneMap Singapore APIs are free and don't require authentication

4. **Run the complete pipeline**:
   ```bash
   python main.py
   ```

## 📊 Data Sources

### Google Maps API
Extracts fitness locations with the following fields:
- Name, Place ID, Address
- Latitude/Longitude coordinates
- Rating and review count
- Website and phone number
- Business category

**Search Keywords**: 45+ fitness-related terms including gym, yoga, pilates, martial arts, dance studios, etc.

### OneMap Singapore API
- **Planning Areas**: All 55 planning areas with polygon coordinates
- **Household Income**: Monthly household income data for each planning area (2020 data)

## 🎨 Visualization Features

### Interactive Map (`singapore_fitness_map.html`)
- **Color-coded categories**: Each fitness type has a distinct color
- **Detailed popups**: Business information, ratings, income data
- **Layer controls**: Toggle different categories on/off
- **Income heatmap**: Visual representation of household income
- **Statistics panel**: Real-time summary statistics

### Analysis Report (`fitness_analysis_report.html`)
- **Category breakdown**: Distribution of fitness business types
- **Top-rated locations**: Best-rated fitness studios
- **Income analysis**: Average income by category and area
- **Statistical summaries**: Comprehensive data insights

## 🛠️ Usage Options

### Complete Pipeline
```bash
python main.py
```

### Skip Google Maps Extraction (use existing data)
```bash
python main.py --skip-google
```

### Skip OneMap Extraction (use existing data)
```bash
python main.py --skip-onemap
```

### Data extraction only (skip visualization)
```bash
python main.py --data-only
```

### Skip visualization (data processing only)
```bash
python main.py --skip-visualization
```

## 📈 Fitness Categories

The system automatically categorizes locations into:

1. **BFT** - BodyFit Training studios
2. **Fitness Studio** - General fitness and training studios
3. **Yoga/Pilates Studio** - Yoga, pilates, and related studios
4. **Gym** - Traditional gyms and fitness centers
5. **Martial Arts** - Boxing, MMA, BJJ, karate, etc.
6. **Dance Studio** - Dance, Zumba, barre, pole studios
7. **Cycling/Spin** - Indoor cycling and spin studios
8. **Others** - Miscellaneous fitness businesses

## 🔧 Configuration

### API Configuration (`config.py`)
- Google Maps API key
- OneMap API endpoints
- Singapore geographic bounds
- Fitness search keywords
- Output file paths

### Customization Options
- Add new fitness keywords in `FITNESS_KEYWORDS`
- Modify category definitions in `data_processor.py`
- Adjust map styling in `visualization.py`
- Change data sources or years

## 📊 Output Files

### Data Files (`data/` directory)
- `fitness_locations.csv` - Raw Google Maps data
- `planning_areas.csv` - OneMap planning areas
- `household_income.csv` - Processed income data
- `combined_data.csv` - Final combined dataset

### Visualization Files
- `singapore_fitness_map.html` - Interactive map
- `fitness_analysis_report.html` - Analysis report

## 🔍 Data Processing

### Income Calculation
- Uses weighted averages for income ranges
- Midpoint calculation for income brackets
- Handles "SGD 20,000 and over" as $20,000

### Location Categorization
- Keyword-based automatic categorization
- Fallback to "Others" for uncategorized locations
- Based on business name and search query

### Geographic Assignment
- Planning areas assigned based on nearest centroid
- Singapore bounds filtering
- Coordinate validation

## 🚨 Rate Limiting

The system includes built-in rate limiting:
- Google Maps API: 0.1s delay between requests
- OneMap API: 0.5s delay between requests
- Respectful API usage to avoid quotas

## 📝 Troubleshooting

### Common Issues

1. **API Quota Exceeded**
   - Check Google Maps API usage
   - Use `--skip-google` to use existing data

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **No Data Found**
   - Verify internet connection
   - Check API key validity
   - Review search keywords in config

4. **Map Not Loading**
   - Open HTML files in modern web browser
   - Check browser console for errors
   - Ensure JavaScript is enabled

## 🤝 Contributing

To extend the project:

1. **Add New Categories**: Modify `fitness_categories` in `data_processor.py`
2. **New Data Sources**: Create new extractor modules
3. **Enhanced Visualization**: Extend `visualization.py`
4. **Additional Analysis**: Add new analysis functions

## 📄 License

This project is for educational and research purposes. Please respect the terms of service for:
- Google Maps Platform API
- OneMap Singapore API

## 🙏 Acknowledgments

- **Google Maps Platform** for location data
- **OneMap Singapore** for planning areas and income data
- **Folium** for interactive map creation
- **Pandas** for data processing

---

**Note**: This project extracts publicly available data for analysis purposes. Please ensure compliance with all API terms of service and data usage policies.
