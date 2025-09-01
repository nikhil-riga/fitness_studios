import pandas as pd
import os
from config import COMBINED_DATA_OUTPUT

def better_data_cleaner():
    """
    Clean fitness data by excluding non-fitness locations while preserving legitimate fitness businesses
    """
    print("Starting better data cleaning process...")
    
    if not os.path.exists(COMBINED_DATA_OUTPUT):
        print(f"Combined data file not found: {COMBINED_DATA_OUTPUT}")
        return
    
    df = pd.read_csv(COMBINED_DATA_OUTPUT)
    print(f"Loaded {len(df)} total locations")
    
    # Define legitimate fitness business keywords (these should be KEPT)
    legitimate_fitness_keywords = [
        'anytime fitness', 'the gym pod', 'bft', 'f45', 'labx', 'vitality pod', 
        'gold\'s gym', 'the pilates lab', 'yoga', 'pilates', 'martial arts', 
        'taekwon-do', 'taekwondo', 'karate', 'parkour', 'gym', 'fitness', 
        'training', 'workout', 'exercise', 'strength', 'cardio', 'hiit', 
        'crossfit', 'boxing', 'mma', 'jiu-jitsu', 'bjj', 'muay thai', 
        'kickboxing', 'judo', 'aikido', 'kung fu', 'wing chun', 'silat',
        'dance', 'zumba', 'ballet', 'jazz', 'contemporary', 'pole', 'aerial',
        'cycling', 'spin', 'rhythm', 'indoor cycling', 'soulcycle', 'peloton',
        'barre', 'reformer', 'megaformer', 'lagree', 'bikram', 'hot yoga',
        'power yoga', 'hatha', 'vinyasa', 'ashtanga', 'iyengar', 'kundalini',
        'meditation', 'mindfulness', 'personal training', 'pt', 'trainer',
        'coach', 'fitness studio', 'health club', 'sports club', 'athletic club'
    ]
    
    # Define exclusion keywords (these should be REMOVED)
    exclusion_keywords = [
        'alumni', 'arts', 'gardens', 'community club', 'store', 'sikh', 'park', 
        'underpass', 'temple', 'community', 'civil service', 'sports centre',
        'fitness corner', 'country club',
        'school', 'college', 'university', 'institute', 'academy', 'education',
        'hospital', 'clinic', 'medical', 'healthcare', 'pharmacy', 'dental',
        'hotel', 'resort', 'spa', 'wellness center', 'retreat', 'massage',
        'restaurant', 'cafe', 'food', 'dining', 'bar', 'pub', 'club',
        'bank', 'financial', 'insurance', 'real estate', 'property',
        'shopping', 'mall', 'retail', 'fashion', 'beauty', 'salon',
        'swimming', 'pool', 'aquatic', 'water sports',
        'childcare', 'kindergarten', 'preschool', 'daycare',
        'equipment', 'supplies', 'rental', 'sales', 'service',
        'private', 'individual', 'one-on-one',
        'basic', 'fundamental', 'beginner', 'advanced',
        'manager', 'director', 'coordinator', 'administrator',
        'security', 'guard', 'protection', 'safety',
        'delivery', 'pickup', 'drop-off', 'transport',
        'maintenance', 'repair', 'service', 'support',
        'consulting', 'advisory', 'consultation', 'advice',
        'research', 'study', 'analysis', 'assessment',
        'government', 'public', 'municipal', 'council',
        'religious', 'church', 'mosque', 'synagogue', 'worship',
        'social', 'welfare', 'charity',
        'recreation', 'leisure',
        'outdoor', 'adventure', 'camping', 'hiking',
        'indoor', 'space', 'venue', 'facility'
    ]
    
    def should_exclude(name):
        if pd.isna(name):
            return False
        
        name_lower = str(name).lower()
        
        # First check if it contains legitimate fitness keywords - if so, KEEP it
        for keyword in legitimate_fitness_keywords:
            if keyword in name_lower:
                return False
        
        # Then check if it contains exclusion keywords - if so, REMOVE it
        # But be more careful about certain keywords that might be part of legitimate fitness names
        for keyword in exclusion_keywords:
            if keyword in name_lower:
                # Special cases where we should NOT exclude even if they contain exclusion keywords
                if keyword == 'clinic' and ('ufit' in name_lower or 'fitness' in name_lower):
                    return False
                if keyword == 'mall' and ('fitness' in name_lower or 'gym' in name_lower):
                    return False
                if keyword == 'club' and ('fitness' in name_lower or 'gym' in name_lower or 'sports' in name_lower):
                    return False
                if keyword == 'bar' and ('barry' in name_lower or 'fitness' in name_lower):
                    return False
                return True
        
        # If it doesn't contain fitness keywords but also doesn't contain exclusion keywords,
        # we need to be more careful - let's check the category
        return False
    
    # Apply the better exclusion logic
    excluded_df = df[df['name'].apply(should_exclude)].copy()
    remaining_df = df[~df['name'].apply(should_exclude)].copy()
    
    print(f"\nBetter exclusions applied:")
    print(f"Excluded {len(excluded_df)} non-fitness locations")
    print(f"Kept {len(remaining_df)} legitimate fitness locations")
    
    # Show examples of excluded locations
    print(f"\nExamples of excluded locations:")
    for i, row in excluded_df.head(10).iterrows():
        print(f"- {row['name']} ({row['category']})")
    
    # Show examples of kept locations
    print(f"\nExamples of kept locations:")
    for i, row in remaining_df.head(10).iterrows():
        print(f"- {row['name']} ({row['category']})")
    
    # Save results
    excluded_output = "data/better_excluded_locations.csv"
    excluded_df.to_csv(excluded_output, index=False)
    print(f"\nExcluded locations saved to: {excluded_output}")
    
    remaining_output = "data/better_cleaned_locations.csv"
    remaining_df.to_csv(remaining_output, index=False)
    print(f"Cleaned locations saved to: {remaining_output}")
    
    # Show category distribution after cleaning
    print(f"\nCategory distribution after better cleaning:")
    category_counts = remaining_df['category'].value_counts()
    for category, count in category_counts.items():
        print(f"- {category}: {count}")
    
    return remaining_df, excluded_df

if __name__ == "__main__":
    better_data_cleaner()
