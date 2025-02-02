"""Event handlers for input components."""

import os
from podcastfy.client import generate_podcast
from ..components.input import analyze_content
from ..components.style import create_conversation_config
from ..components.longform import create_chunk_config
from ..config.settings import AUDIO_DIR, TRANSCRIPTS_DIR

def preview_transcript(text_input, url_input, file_input, style, role1, role2, engagement_techniques, longform_enabled, chunk_size, num_chunks):
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
        elif file_input:
            # Determine file type
            file_path = file_input
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                transcript_file = generate_podcast(
                    image_paths=[file_path],
                    transcript_only=True,
                    longform=longform_enabled,
                    conversation_config=config
                )
            elif file_path.lower().endswith('.pdf'):
                transcript_file = generate_podcast(
                    urls=[file_path],  # PDF extractor handles this
                    transcript_only=True,
                    longform=longform_enabled,
                    conversation_config=config
                )
            elif file_path.lower().endswith('.txt'):
                with open(file_path, 'r') as f:
                    content = f.read()
                transcript_file = generate_podcast(
                    text=content,
                    transcript_only=True,
                    longform=longform_enabled,
                    conversation_config=config
                )
            else:
                return "Unsupported file type. Please upload an image (.jpg, .jpeg, .png), PDF, or text file."
        else:
            return "Please provide input via text, URL, or file upload."
        
        # Read generated transcript
        with open(transcript_file, 'r') as f:
            transcript = f.read()
            
        return transcript
    except Exception as e:
        return f"Error generating transcript: {str(e)}"

def update_content_analysis(text, url, config_name):
    """Handle content analysis updates."""
    return analyze_content(text, url, config_name)
