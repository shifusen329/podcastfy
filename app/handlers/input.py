"""Event handlers for input components."""

import os
from podcastfy.client import generate_podcast
from ..components.input import analyze_content
from ..components.style import create_conversation_config
from ..components.longform import create_chunk_config
from ..config.settings import AUDIO_DIR, TRANSCRIPTS_DIR

def preview_transcript(text_input, url_input, style, role1, role2, engagement_techniques, longform_enabled, chunk_size, num_chunks):
    """Handle transcript preview generation."""
    try:
        # Create conversation config
        config = create_conversation_config(style, role1, role2, engagement_techniques)
        
        # Add longform settings if enabled
        if longform_enabled:
            config.update(create_chunk_config(longform_enabled, chunk_size, num_chunks))
        
        # Generate transcript
        if text_input:
            transcript_file = generate_podcast(
                text=text_input,
                transcript_only=True,
                longform=longform_enabled,
                conversation_config=config
            )
        elif url_input:
            transcript_file = generate_podcast(
                urls=[url_input],
                transcript_only=True,
                longform=longform_enabled,
                conversation_config=config
            )
        else:
            return "Please provide either text or URL input."
        
        # Read generated transcript
        with open(transcript_file, 'r') as f:
            transcript = f.read()
            
        return transcript
    except Exception as e:
        return f"Error generating transcript: {str(e)}"

def update_content_analysis(text, url, config_name):
    """Handle content analysis updates."""
    return analyze_content(text, url, config_name)
