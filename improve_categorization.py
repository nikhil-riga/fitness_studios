import pandas as pd
import os

def improve_categorization():
    """
    Improve categorization of fitness businesses by analyzing their names
    """
    print("Improving fitness business categorization...")
    
    # Load the targeted cleaned data
    cleaned_data_path = "data/better_cleaned_locations.csv"
    if not os.path.exists(cleaned_data_path):
        print(f"Cleaned data file not found: {cleaned_data_path}")
        return
    
    df = pd.read_csv(cleaned_data_path)
    print(f"Loaded {len(df)} cleaned locations")
    
    # Define keywords for better categorization
    yoga_pilates_keywords = [
        'yoga', 'pilates', 'reformer', 'megaformer', 'lagree', 'bikram', 'yin', 'aerial yoga',
        'hot yoga', 'power yoga', 'hatha', 'vinyasa', 'ashtanga', 'iyengar', 'kundalini',
        'meditation', 'mindfulness', 'zen', 'om', 'namaste', 'shanti', 'prana'
    ]
    
    martial_arts_keywords = [
        'martial', 'karate', 'taekwondo', 'judo', 'jiu-jitsu', 'bjj', 'muay thai', 'kickboxing',
        'boxing', 'mma', 'krav maga', 'silat', 'kung fu', 'wing chun', 'aikido', 'hapkido',
        'wrestling', 'grappling', 'combat', 'fight', 'strike', 'punch', 'kick'
    ]
    
    cycling_spin_keywords = [
        'cycling', 'spin', 'rhythm', 'indoor cycling', 'bike', 'peloton', 'soulcycle',
        'flywheel', 'cyclebar', 'spinning', 'bicycle', 'wheel', 'pedal'
    ]
    
    dance_keywords = [
        'dance', 'zumba', 'contemporary', 'pole', 'aerial', 'ballet', 'jazz', 'hip hop',
        'salsa', 'bachata', 'kizomba', 'ballroom', 'latin', 'street dance', 'urban dance',
        'barre', 'ballet barre', 'dance studio', 'choreography'
    ]
    
    bft_keywords = [
        'bft', 'body fit training', 'bodyfit', 'body fit', 'bf training'
    ]
    
    gym_keywords = [
        'gym', 'fitness center', 'fitness centre', 'health club', 'sports club',
        'athletic club', 'fitness club', 'gymnasium', 'weight room', 'strength training',
        'powerlifting', 'weightlifting', 'bodybuilding', 'crossfit', 'functional training',
        'strength', 'power', 'muscle', 'bodybuilding'
    ]
    
    # Function to categorize based on name
    def categorize_business(name, current_category):
        if pd.isna(name):
            return current_category
        
        name_lower = str(name).lower()
        
        # Check for specific keywords and override category
        for keyword in yoga_pilates_keywords:
            if keyword in name_lower:
                return 'Yoga/Pilates Studio'
        
        for keyword in martial_arts_keywords:
            if keyword in name_lower:
                return 'Martial Arts'
        
        for keyword in cycling_spin_keywords:
            if keyword in name_lower:
                return 'Cycling/Spin'
        
        for keyword in dance_keywords:
            if keyword in name_lower:
                return 'Dance Studio'
        
        for keyword in bft_keywords:
            if keyword in name_lower:
                return 'BFT'
        
        for keyword in gym_keywords:
            if keyword in name_lower:
                return 'Gym'
        
        return current_category
    
    # Apply improved categorization
    df['improved_category'] = df.apply(
        lambda row: categorize_business(row['name'], row['category']), 
        axis=1
    )
    
    # Show categorization changes
    print("\nCategorization improvements:")
    changes = df[df['category'] != df['improved_category']]
    print(f"Found {len(changes)} businesses that need recategorization:")
    
    for idx, row in changes.head(20).iterrows():
        print(f"- {row['name']}: {row['category']} → {row['improved_category']}")
    
    # Show final category distribution
    print(f"\nFinal category distribution:")
    category_counts = df['improved_category'].value_counts()
    for category, count in category_counts.items():
        print(f"- {category}: {count}")
    
    # Save improved data
    improved_output = "data/better_final_fitness_locations.csv"
    df.to_csv(improved_output, index=False)
    print(f"\nBetter final improved data saved to: {improved_output}")
    
    # Create a summary of what was changed
    print(f"\nSummary of changes:")
    for category in df['improved_category'].unique():
        old_count = len(df[df['category'] == category])
        new_count = len(df[df['improved_category'] == category])
        if old_count != new_count:
            print(f"- {category}: {old_count} → {new_count} ({new_count - old_count:+d})")
    
    return df

if __name__ == "__main__":
    improve_categorization()
