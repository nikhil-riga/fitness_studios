import pandas as pd
import os
from config import COMBINED_DATA_OUTPUT

def targeted_data_cleaner():
    """
    Clean fitness data using targeted exclusion keywords and suggest additional ones
    """
    print("Starting targeted data cleaning process...")
    
    if not os.path.exists(COMBINED_DATA_OUTPUT):
        print(f"Combined data file not found: {COMBINED_DATA_OUTPUT}")
        return
    
    df = pd.read_csv(COMBINED_DATA_OUTPUT)
    print(f"Loaded {len(df)} total locations")
    
    # User-specified exclusion keywords
    user_exclude_keywords = [
        'alumni', 'arts', 'gardens', 'community club', 'store', 'sikh', 'park', 'underpass', 'temple',
        'community', 'civil service', 'sports centre'
    ]
    
    # Function to check if location should be excluded
    def should_exclude(name):
        if pd.isna(name):
            return False
        name_lower = str(name).lower()
        return any(keyword in name_lower for keyword in user_exclude_keywords)
    
    # Apply user exclusions
    excluded_df = df[df['name'].apply(should_exclude)].copy()
    remaining_df = df[~df['name'].apply(should_exclude)].copy()
    
    print(f"\nUser exclusions applied:")
    print(f"Excluded {len(excluded_df)} locations with user-specified keywords")
    print(f"Remaining {len(remaining_df)} locations")
    
    # Show examples of excluded locations
    print(f"\nExamples of excluded locations:")
    for i, row in excluded_df.head(10).iterrows():
        print(f"- {row['name']} ({row['category']})")
    
    # Analyze remaining data for potential additional exclusions
    print(f"\nAnalyzing remaining data for potential additional exclusions...")
    
    # Look for patterns in the remaining data that might be non-fitness related
    potential_exclusions = []
    
    # Check for common non-fitness terms in remaining data
    non_fitness_patterns = [
        'school', 'college', 'university', 'institute', 'academy', 'education',
        'hospital', 'clinic', 'medical', 'healthcare', 'pharmacy', 'dental',
        'hotel', 'resort', 'spa', 'wellness center', 'retreat', 'massage',
        'restaurant', 'cafe', 'food', 'dining', 'bar', 'pub', 'club',
        'bank', 'financial', 'insurance', 'real estate', 'property',
        'shopping', 'mall', 'retail', 'fashion', 'beauty', 'salon',
        'swimming', 'pool', 'aquatic', 'water sports',
        'childcare', 'kindergarten', 'preschool', 'daycare',
        'equipment', 'supplies', 'rental', 'sales', 'service',
        'training', 'course', 'workshop', 'seminar', 'class',
        'private', 'personal', 'individual', 'one-on-one',
        'basic', 'fundamental', 'beginner', 'advanced',
        'instructor', 'trainer', 'coach', 'teacher',
        'manager', 'director', 'coordinator', 'administrator',
        'security', 'guard', 'protection', 'safety',
        'delivery', 'pickup', 'drop-off', 'transport',
        'maintenance', 'repair', 'service', 'support',
        'consulting', 'advisory', 'consultation', 'advice',
        'research', 'study', 'analysis', 'assessment',
        'government', 'public', 'municipal', 'council',
        'religious', 'church', 'mosque', 'synagogue', 'worship',
        'community', 'social', 'welfare', 'charity',
        'sports', 'athletic', 'recreation', 'leisure',
        'outdoor', 'adventure', 'camping', 'hiking',
        'indoor', 'studio', 'space', 'venue', 'facility'
    ]
    
    # Check which patterns appear in the remaining data
    for pattern in non_fitness_patterns:
        pattern_matches = remaining_df[remaining_df['name'].str.lower().str.contains(pattern, na=False)]
        if len(pattern_matches) > 0:
            potential_exclusions.append({
                'pattern': pattern,
                'count': len(pattern_matches),
                'examples': pattern_matches['name'].head(3).tolist()
            })
    
    # Sort by count and show top suggestions
    potential_exclusions.sort(key=lambda x: x['count'], reverse=True)
    
    print(f"\nPotential additional exclusion keywords (showing top 20):")
    print("=" * 80)
    for i, item in enumerate(potential_exclusions[:20]):
        print(f"{i+1:2d}. '{item['pattern']}' - {item['count']} matches")
        print(f"    Examples: {', '.join(item['examples'])}")
        print()
    
    # Save results
    excluded_output = "data/targeted_excluded_locations.csv"
    excluded_df.to_csv(excluded_output, index=False)
    print(f"Excluded locations saved to: {excluded_output}")
    
    remaining_output = "data/targeted_cleaned_locations.csv"
    remaining_df.to_csv(remaining_output, index=False)
    print(f"Cleaned locations saved to: {remaining_output}")
    
    # Show category distribution after cleaning
    print(f"\nCategory distribution after targeted cleaning:")
    category_counts = remaining_df['category'].value_counts()
    for category, count in category_counts.items():
        print(f"- {category}: {count}")
    
    return remaining_df, excluded_df, potential_exclusions

if __name__ == "__main__":
    targeted_data_cleaner()
