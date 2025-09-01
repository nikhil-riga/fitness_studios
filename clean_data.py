import pandas as pd
import os
from config import COMBINED_DATA_OUTPUT

def clean_fitness_data():
    """
    Clean fitness data by removing unwanted categories and creating separate CSV for review
    """
    print("Starting data cleaning process...")
    
    # Load the combined data
    if not os.path.exists(COMBINED_DATA_OUTPUT):
        print(f"Combined data file not found: {COMBINED_DATA_OUTPUT}")
        return
    
    df = pd.read_csv(COMBINED_DATA_OUTPUT)
    print(f"Loaded {len(df)} total locations")
    
    # Create a copy for filtering
    original_df = df.copy()
    
    # Define keywords to exclude
    exclude_keywords = [
        'alumni', 'arts', 'gardens', 'community clubs', 'store',
        'school', 'college', 'university', 'institute', 'academy',
        'hospital', 'clinic', 'medical', 'healthcare', 'pharmacy',
        'hotel', 'resort', 'spa', 'wellness center', 'retreat',
        'church', 'temple', 'mosque', 'religious',
        'library', 'museum', 'gallery', 'theater',
        'restaurant', 'cafe', 'bar', 'pub', 'food',
        'bank', 'insurance', 'financial', 'office',
        'shopping', 'mall', 'market', 'supermarket',
        'transport', 'bus', 'train', 'station',
        'government', 'council', 'ministry', 'agency',
        'police', 'fire', 'emergency', 'security',
        'construction', 'building', 'development',
        'park', 'playground', 'recreation', 'sports complex',
        'swimming', 'tennis', 'golf', 'football', 'soccer',
        'badminton', 'table tennis', 'squash',
        'bowling', 'arcade', 'entertainment',
        'childcare', 'kindergarten', 'preschool',
        'senior', 'elderly', 'retirement',
        'disability', 'special needs',
        'youth', 'teen', 'adolescent',
        'women only', 'men only', 'ladies', 'gentlemen',
        'corporate', 'business', 'commercial',
        'residential', 'apartment', 'condo', 'housing',
        'industrial', 'factory', 'warehouse',
        'agriculture', 'farm', 'garden',
        'veterinary', 'pet', 'animal',
        'automotive', 'car', 'vehicle',
        'electronics', 'computer', 'technology',
        'furniture', 'home', 'household',
        'clothing', 'fashion', 'apparel',
        'jewelry', 'accessories',
        'beauty', 'salon', 'cosmetics',
        'dental', 'orthodontist', 'dentist',
        'optical', 'eyewear', 'glasses',
        'hearing', 'audiology',
        'physiotherapy', 'occupational therapy', 'speech therapy',
        'nutrition', 'dietitian', 'nutritionist',
        'psychology', 'counseling', 'therapy',
        'massage', 'reflexology', 'acupuncture',
        'chiropractic', 'osteopathy',
        'traditional', 'herbal', 'alternative',
        'supplements', 'vitamins', 'health food',
        'equipment', 'machinery', 'tools',
        'supplies', 'materials',
        'services', 'consulting', 'advisory',
        'training', 'education', 'course',
        'certification', 'qualification',
        'competition', 'tournament', 'championship',
        'team', 'club', 'association',
        'federation', 'union', 'society',
        'foundation', 'charity', 'non-profit',
        'volunteer', 'community service',
        'research', 'study', 'survey',
        'consultation', 'assessment', 'evaluation',
        'screening', 'testing', 'diagnosis',
        'treatment', 'rehabilitation', 'recovery',
        'prevention', 'maintenance', 'care',
        'support', 'assistance', 'help',
        'guidance', 'advice', 'counseling',
        'mentoring', 'coaching', 'tutoring',
        'workshop', 'seminar', 'conference',
        'event', 'program', 'activity',
        'class', 'lesson', 'session',
        'appointment', 'booking', 'reservation',
        'membership', 'subscription', 'package',
        'deal', 'offer', 'promotion',
        'discount', 'sale', 'clearance',
        'rental', 'hire', 'lease',
        'purchase', 'buy', 'sell',
        'trade', 'exchange', 'swap',
        'donation', 'contribution', 'fundraising',
        'sponsorship', 'partnership', 'collaboration',
        'affiliation', 'alliance', 'network',
        'franchise', 'chain', 'brand',
        'independent', 'local', 'family',
        'boutique', 'specialty', 'niche',
        'premium', 'luxury', 'exclusive',
        'budget', 'economy', 'affordable',
        'high-end', 'elite', 'prestigious',
        'award-winning', 'recognized', 'accredited',
        'licensed', 'certified', 'registered',
        'insured', 'bonded', 'guaranteed',
        'warranty', 'guarantee', 'assurance',
        'refund', 'return', 'exchange',
        'delivery', 'pickup', 'shipping',
        'installation', 'setup', 'assembly',
        'maintenance', 'repair', 'service',
        'cleaning', 'sanitization', 'disinfection',
        'inspection', 'audit', 'review',
        'monitoring', 'tracking', 'surveillance',
        'security', 'safety', 'protection',
        'emergency', 'urgent', 'critical',
        'priority', 'vip', 'premium',
        'exclusive', 'private', 'confidential',
        'personal', 'individual', 'custom',
        'tailored', 'bespoke', 'made-to-order',
        'standard', 'regular', 'normal',
        'basic', 'essential', 'fundamental',
        'advanced', 'professional', 'expert',
        'specialist', 'consultant', 'advisor',
        'instructor', 'trainer', 'coach',
        'teacher', 'educator', 'facilitator',
        'leader', 'director', 'manager',
        'supervisor', 'coordinator', 'organizer',
        'administrator', 'coordinator', 'liaison',
        'representative', 'agent', 'broker',
        'intermediary', 'middleman', 'go-between',
        'facilitator', 'enabler', 'supporter',
        'helper', 'assistant', 'aide',
        'attendant', 'caregiver', 'nurse',
        'therapist', 'counselor', 'advisor',
        'mentor', 'guide', 'tutor',
        'instructor', 'teacher', 'educator',
        'trainer', 'coach', 'facilitator',
        'leader', 'director', 'manager',
        'supervisor', 'coordinator', 'organizer',
        'administrator', 'coordinator', 'liaison',
        'representative', 'agent', 'broker',
        'intermediary', 'middleman', 'go-between',
        'facilitator', 'enabler', 'supporter',
        'helper', 'assistant', 'aide',
        'attendant', 'caregiver', 'nurse',
        'therapist', 'counselor', 'advisor',
        'mentor', 'guide', 'tutor'
    ]
    
    # Create a function to check if any exclude keyword is in the name
    def should_exclude(name):
        if pd.isna(name):
            return False
        name_lower = str(name).lower()
        return any(keyword in name_lower for keyword in exclude_keywords)
    
    # Filter out unwanted locations
    excluded_df = df[df['name'].apply(should_exclude)].copy()
    cleaned_df = df[~df['name'].apply(should_exclude)].copy()
    
    print(f"Excluded {len(excluded_df)} locations with unwanted keywords")
    print(f"Remaining {len(cleaned_df)} locations after cleaning")
    
    # Save excluded locations for review
    excluded_output = "data/excluded_locations.csv"
    excluded_df.to_csv(excluded_output, index=False)
    print(f"Excluded locations saved to: {excluded_output}")
    
    # Save cleaned data
    cleaned_output = "data/cleaned_fitness_locations.csv"
    cleaned_df.to_csv(cleaned_output, index=False)
    print(f"Cleaned locations saved to: {cleaned_output}")
    
    # Show some examples of excluded locations
    print("\nExamples of excluded locations:")
    for i, row in excluded_df.head(10).iterrows():
        print(f"- {row['name']} ({row['category']})")
    
    # Show category distribution after cleaning
    print(f"\nCategory distribution after cleaning:")
    category_counts = cleaned_df['category'].value_counts()
    for category, count in category_counts.items():
        print(f"- {category}: {count}")
    
    return cleaned_df, excluded_df

if __name__ == "__main__":
    clean_fitness_data()

