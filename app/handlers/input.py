"""Event handlers for input components."""

import os
import tempfile
from podcastfy.client import generate_podcast
from podcastfy.content_parser.content_extractor import ContentExtractor
from .style import create_conversation_config
from ..components.longform import create_chunk_config
from ..config.settings import AUDIO_DIR, TRANSCRIPTS_DIR

def process_multiple_urls(url_input: str) -> str:
    """Convert multiple URLs to temporary file."""
    if not url_input.strip():
        return None
    # Split URLs by newline and filter empty lines
    urls = [url.strip() for url in url_input.split('\n') if url.strip()]
    if not urls:
        return None
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('\n'.join(urls))
        return f.name

def preview_transcript(text_input, url_input, file_input, directory_input, recursive, file_types, style, role1, role2, engagement_techniques, longform_enabled, chunk_size, num_chunks):
    """Handle transcript preview generation."""
    try:
        # Create conversation config
        config = create_conversation_config(style, role1, role2, engagement_techniques)
        
        # Add longform settings if enabled
        if longform_enabled:
            config.update(create_chunk_config(longform_enabled, chunk_size, num_chunks))
        
        # Process directory input
        if directory_input:
            # Use content extractor to process directory
            content_extractor = ContentExtractor()
            directory_content = content_extractor.extract_from_directory(
                directory=directory_input,
                recursive=recursive,
                file_types=file_types if "All Files" not in file_types else None
            )
            # Pass as text input to generate_podcast
            transcript_file = generate_podcast(
                text=directory_content,
                transcript_only=True,
                longform=longform_enabled,
                conversation_config=config
            )
        # Process text input (includes topics)
        elif text_input:
            transcript_file = generate_podcast(
                text=text_input,
                transcript_only=True,
                longform=longform_enabled,
                conversation_config=config
            )
        # Process URL input (multiple URLs)
        elif url_input:
            url_file = process_multiple_urls(url_input)
            if url_file:
                with open(url_file, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
                transcript_file = generate_podcast(
                    urls=urls,
                    transcript_only=True,
                    longform=longform_enabled,
                    conversation_config=config
                )
                os.unlink(url_file)  # Clean up temporary file
            else:
                return "Please provide valid URLs, one per line."
        # Process file input
        elif file_input:
            # Handle multiple files
            image_paths = []
            text_content = []
            urls = []
            
            for file_path in file_input:
                if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_paths.append(file_path)
                elif file_path.lower().endswith('.pdf'):
                    urls.append(file_path)  # PDF extractor handles this
                elif file_path.lower().endswith('.txt'):
                    with open(file_path, 'r') as f:
                        text_content.append(f.read())
                else:
                    return f"Unsupported file type: {file_path}"
            
            # Generate podcast with all inputs
            transcript_file = generate_podcast(
                text="\n\n".join(text_content) if text_content else None,
                urls=urls if urls else None,
                image_paths=image_paths if image_paths else None,
                transcript_only=True,
                longform=longform_enabled,
                conversation_config=config
            )
        else:
            return "Please provide input via text, URL, file upload, or directory path."
        
        # Read generated transcript
        with open(transcript_file, 'r') as f:
            transcript = f.read()
            
        return transcript
    except Exception as e:
        return f"Error generating transcript: {str(e)}"
