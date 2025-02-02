"""General settings and configuration for the Podcastfy UI."""

# Longform configuration presets
CHUNK_CONFIGS = {
    'default': {
        'max_num_chunks': 7,
        'min_chunk_size': 600,
        'description': 'Default settings (15-20 min podcast)'
    },
    'medium': {
        'max_num_chunks': 10,
        'min_chunk_size': 800,
        'description': 'Medium length (20-25 min podcast)'
    },
    'long': {
        'max_num_chunks': 15,
        'min_chunk_size': 1000,
        'description': 'Long format (30+ min podcast)'
    }
}

# TTS model settings
TTS_MODELS = [
    "openai",
    "elevenlabs",
    "edge",
    "gemini",
    "geminimulti",
    "kokoro",
    "novel-ai"
]

# Supported languages
LANGUAGES = [
    "English",
    "French",
    "Portuguese"
]

# File paths
DATA_DIR = "data"
AUDIO_DIR = f"{DATA_DIR}/audio"
TRANSCRIPTS_DIR = f"{DATA_DIR}/transcripts"

# Content analysis thresholds
CONTENT_LENGTH_THRESHOLDS = {
    'short': 1000,    # <1000 chars: 1-2 minutes
    'medium': 20000,  # <20000 chars: 18-21 minutes
    'long': 50000    # >50000 chars: 20-23 minutes
}

# Processing time estimates
PROCESSING_TIME_ESTIMATES = {
    'short': "~20 seconds",
    'medium': "4-5 minutes",
    'long': "5-6 minutes"
}

# Duration estimates
DURATION_ESTIMATES = {
    'short': "1-2 minutes",
    'medium': "18-21 minutes",
    'long': "20-23 minutes"
}
