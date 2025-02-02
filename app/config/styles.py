"""Configuration for conversation styles and engagement techniques."""

# Available formats
FORMATS = {
    "conversation": {
        "name": "Conversation",
        "description": "Two-person dialogue format",
        "roles": ["Host", "Guest"],
        "supports_roles": True
    },
    "monologue": {
        "name": "Monologue",
        "description": "Single-speaker narrative",
        "roles": ["Narrator"],
        "supports_roles": False
    }
}

# Predefined styles by format
STYLES = {
    'conversation': {
        'engaging': {
            'conversation_style': ['Engaging', 'Enthusiastic'],
            'engagement_techniques': ['Rhetorical Questions', 'Personal Testimonials', 'Humor'],
            'roles_person1': 'Curious Host',
            'roles_person2': 'Subject Matter Expert'
        },
        'educational': {
            'conversation_style': ['Educational', 'Formal'],
            'engagement_techniques': ['Facts', 'Historical Context', 'Expert Opinions'],
            'roles_person1': 'History Professor',
            'roles_person2': 'Armchair Historian'
        },
        'casual': {
            'conversation_style': ['Casual', 'Friendly'],
            'engagement_techniques': ['Humor', 'Anecdotes', 'Real-world Examples'],
            'roles_person1': 'Enthusiast',
            'roles_person2': 'Novice'
        },
        'analytical': {
            'conversation_style': ['Analytical', 'Technical'],
            'engagement_techniques': ['Facts', 'Case Studies', 'Statistics'],
            'roles_person1': 'Industry Analyst',
            'roles_person2': 'Domain Expert'
        },
        'storytelling': {
            'conversation_style': ['Narrative', 'Descriptive'],
            'engagement_techniques': ['Anecdotes', 'Historical Context', 'Personal Testimonials'],
            'roles_person1': 'Storyteller',
            'roles_person2': 'Historical Figure'
        },
        'debate': {
            'conversation_style': ['Critical', 'Balanced'],
            'engagement_techniques': ['Rhetorical Questions', 'Counter Arguments', 'Expert Opinions'],
            'roles_person1': 'Moderator',
            'roles_person2': 'Expert Panelist'
        }
    },
    'monologue': {
        'narrative': {
            'conversation_style': ['Narrative', 'Descriptive'],
            'engagement_techniques': ['Anecdotes', 'Historical Context', 'Personal Testimonials'],
            'roles_person1': 'Narrator'
        },
        'educational': {
            'conversation_style': ['Educational', 'Formal'],
            'engagement_techniques': ['Facts', 'Expert Opinions', 'Case Studies'],
            'roles_person1': 'Narrator'
        },
        'analytical': {
            'conversation_style': ['Analytical', 'Technical'],
            'engagement_techniques': ['Facts', 'Statistics', 'Expert Opinions'],
            'roles_person1': 'Narrator'
        },
        'engaging': {
            'conversation_style': ['Engaging', 'Enthusiastic'],
            'engagement_techniques': ['Rhetorical Questions', 'Anecdotes', 'Humor'],
            'roles_person1': 'Narrator'
        },
        'storytelling': {
            'conversation_style': ['Narrative', 'Descriptive', 'Engaging'],
            'engagement_techniques': ['Anecdotes', 'Historical Context', 'Personal Testimonials', 'Analogies'],
            'roles_person1': 'Narrator'
        },
        'casual': {
            'conversation_style': ['Casual', 'Friendly', 'Conversational'],
            'engagement_techniques': ['Humor', 'Anecdotes', 'Real-world Examples', 'Personal Testimonials'],
            'roles_person1': 'Narrator'
        }
    }
}

# Available engagement techniques
ENGAGEMENT_TECHNIQUES = [
    'Rhetorical Questions',
    'Personal Testimonials',
    'Facts',
    'Historical Context',
    'Humor',
    'Anecdotes',
    'Quotes',
    'Analogies',
    'Case Studies',
    'Counter Arguments',
    'Statistics',
    'Expert Opinions',
    'Real-world Examples',
    'Thought Experiments'
]
