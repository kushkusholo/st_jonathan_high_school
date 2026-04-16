# Configuration file for St. Jonathan High School Chatbot
# Modify this file to update school information without editing the main app

SCHOOL_CONFIG = {
    # School Information
    'name': 'St. Jonathan High School',
    'abbreviation': 'SJHS',
    'address': 'P.O. Box 12352, Kampala',
    'location': 'Jinja-Kampala Highway, next to Mbalala Trading Centre',
    'phone': '+256325516717',
    'phone_alt': '+256312456789',
    'email': 'info@stjonathan.ug',
    'email_admissions': 'admissions@stjonathan.ug',
    'website': 'www.stjonathan.ug',
    'established': 2010,
    
    # Leadership
    'principal': 'Dr. Samuel Mugisha',
    'deputy_principal': 'Ms. Dorothy Nakito',
    'head_academics': 'Mr. James Okwonga',
    
    # Educational Levels
    'levels': ['S.1', 'S.2', 'S.3', 'S.4', 'O-Level'],
    
    # Academic Terms
    'terms': {
        'term_1': {'start': 'January', 'end': 'March'},
        'term_2': {'start': 'April', 'end': 'July'},
        'term_3': {'start': 'August', 'end': 'November'}
    },
    
    # Fees Approximate (in UGX)
    'fees': {
        'S1_2': {
            'min': 2500000,
            'max': 3000000,
            'description': 'Senior 1-2 per term'
        },
        'S3_4': {
            'min': 2800000,
            'max': 3200000,
            'description': 'Senior 3-4 per term'
        },
        'O_Level': {
            'min': 3000000,
            'max': 3500000,
            'description': 'O-Level per term'
        },
        'A_Level': {
            'min': 3500000,
            'max': 4000000,
            'description': 'A-Level (if offered) per term'
        }
    },
    
    # Core Subjects
    'core_subjects': [
        'English Language',
        'Mathematics',
        'Biology',
        'Chemistry',
        'Physics',
        'Kiswahili',
        'History & Social Studies',
        'Physical Education'
    ],
    
    # Optional Subjects
    'optional_subjects': [
        'Computer Science',
        'Geography',
        'Economics',
        'Literature in English',
        'Technical/Vocational Studies',
        'Religious Studies',
        'Fine Art & Design'
    ],
    
    # Facilities
    'facilities': [
        'Science Laboratory (Biology, Chemistry, Physics)',
        'Computer Lab',
        'Library',
        'Sports Field',
        'Basketball Court',
        'Volleyball Court',
        'Dining Hall',
        'Medical Facility',
        'Dormitories (Boys and Girls)',
        'Assembly Hall',
        'Classrooms with Modern Facilities'
    ],
    
    # Extracurricular Activities
    'activities': {
        'sports': ['Football', 'Volleyball', 'Basketball', 'Netball', 'Athletics', 'Swimming', 'Tennis'],
        'clubs': ['Debate', 'Science', 'Environmental', 'Music', 'Drama', 'Photography', 'Computer', 'Leadership'],
        'cultural': ['Dance ensembles', 'Cultural day celebrations', 'Inter-school competitions']
    },
    
    # Contacts by Department
    'departments': {
        'admissions': {
            'phone': '+256325516717',
            'email': 'admissions@stjonathan.ug',
            'officer': 'Mr. Samuel Kimbowa'
        },
        'accounts': {
            'phone': '+256325516717',
            'email': 'accounts@stjonathan.ug',
            'officer': 'Mrs. Beatrice Kamya'
        },
        'academics': {
            'phone': '+256325516717',
            'email': 'academics@stjonathan.ug',
            'officer': 'Mr. James Okwonga'
        },
        'boarding': {
            'phone': '+256325516717',
            'email': 'boarding@stjonathan.ug',
            'boarding_master': 'Mr. Peter Ssewava',
            'boarding_matron': 'Mrs. Grace Namugerire'
        },
        'discipline': {
            'phone': '+256325516717',
            'email': 'discipline@stjonathan.ug',
            'officer': 'Mr. Robert Kamoga'
        }
    },
    
    # Chatbot Settings
    'chatbot': {
        'debug_mode': True,
        'similarity_threshold': 0.3,
        'log_conversations': True,
        'max_log_entries': 1000,
        'response_timeout': 5
    }
}

# Edit the configuration above to customize the chatbot for your school
