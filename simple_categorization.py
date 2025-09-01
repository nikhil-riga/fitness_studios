import pandas as pd
import os

def simple_categorization():
    """
    Simple categorization of fitness businesses based purely on their names
    """
    print("Applying simple categorization based on business names...")
    
    # Load the better cleaned data
    cleaned_data_path = "data/better_cleaned_locations.csv"
    if not os.path.exists(cleaned_data_path):
        print(f"Cleaned data file not found: {cleaned_data_path}")
        return
    
    df = pd.read_csv(cleaned_data_path)
    print(f"Loaded {len(df)} cleaned locations")
    
    def categorize_by_name(name):
        if pd.isna(name):
            return 'Others'
        
        name_lower = str(name).lower()
        
        # Check for specific keywords in order of specificity
        if any(keyword in name_lower for keyword in ['yoga', 'pilates', 'reformer', 'megaformer', 'lagree', 'bikram', 'yin', 'aerial yoga', 'hot yoga', 'power yoga', 'hatha', 'vinyasa', 'ashtanga', 'iyengar', 'kundalini', 'meditation', 'mindfulness']):
            return 'Yoga/Pilates Studio'
        
        if any(keyword in name_lower for keyword in ['martial', 'karate', 'taekwondo', 'judo', 'jiu-jitsu', 'bjj', 'muay thai', 'kickboxing', 'boxing', 'mma', 'krav maga', 'silat', 'kung fu', 'wing chun', 'aikido', 'hapkido', 'wrestling', 'grappling', 'combat', 'fight']):
            return 'Martial Arts'
        
        if any(keyword in name_lower for keyword in ['dance', 'zumba', 'contemporary', 'pole', 'aerial', 'ballet', 'jazz', 'hip hop', 'salsa', 'bachata', 'kizomba', 'ballroom', 'latin', 'street dance', 'urban dance', 'barre', 'ballet barre', 'choreography']):
            return 'Dance Studio'
        
        if any(keyword in name_lower for keyword in ['cycling', 'spin', 'rhythm', 'indoor cycling', 'bike', 'peloton', 'soulcycle', 'flywheel', 'cyclebar', 'spinning', 'bicycle', 'wheel', 'pedal']):
            return 'Cycling/Spin'
        
        if any(keyword in name_lower for keyword in ['bft', 'body fit training', 'bodyfit', 'body fit', 'bf training']):
            return 'BFT'
        
        if any(keyword in name_lower for keyword in ['gym', 'fitness center', 'fitness centre', 'health club', 'sports club', 'athletic club', 'fitness club', 'gymnasium', 'weight room', 'strength training', 'powerlifting', 'weightlifting', 'bodybuilding', 'crossfit', 'functional training', 'strength', 'power', 'muscle']):
            return 'Gym'
        
        if any(keyword in name_lower for keyword in ['fitness', 'training', 'workout', 'exercise', 'cardio', 'hiit', 'personal training', 'pt', 'trainer', 'coach']):
            return 'Fitness Studio'
        
        return 'Others'
    
    # Apply simple categorization
    df['simple_category'] = df['name'].apply(categorize_by_name)
    
    # Show categorization results
    print("\nSimple categorization results:")
    category_counts = df['simple_category'].value_counts()
    for category, count in category_counts.items():
        print(f"- {category}: {count}")
    
    # Show examples of each category
    print(f"\nExamples of each category:")
    for category in df['simple_category'].unique():
        examples = df[df['simple_category'] == category]['name'].head(3).tolist()
        print(f"\n{category}:")
        for example in examples:
            print(f"  - {example}")
    
    # Compare with original categorization
    print(f"\nComparison with original categorization:")
    changes = df[df['category'] != df['simple_category']]
    print(f"Found {len(changes)} businesses with different categorization:")
    
    for idx, row in changes.head(10).iterrows():
        print(f"- {row['name']}: {row['category']} → {row['simple_category']}")
    
    # Save the data with simple categorization
    output_path = "data/simple_categorized_locations.csv"
    df.to_csv(output_path, index=False)
    print(f"\nSimple categorized data saved to: {output_path}")
    
    return df

if __name__ == "__main__":
    simple_categorization()

