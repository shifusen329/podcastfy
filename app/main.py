"""Main Gradio interface for Podcastfy."""

import gradio as gr
import os
from podcastfy.client import generate_podcast

# Import components
from .components.input import create_input_components
from .components.style import create_style_components
from .components.longform import create_longform_components
from .components.voice import create_voice_components
from .components.progress import create_progress_components, update_progress

# Import handlers
from .handlers.style import update_style_fields, validate_style_config
from .handlers.longform import update_chunk_sliders, toggle_longform_controls
from .handlers.voice import update_voice_choices, sample_voice, generate_audio
from .handlers.progress import start_progress, update_generation_progress, end_progress
from .handlers.input import process_multiple_urls
from podcastfy.content_parser.content_extractor import ContentExtractor

# Import utilities
from .utils.directory import combine_directory_texts, is_text_directory

def create_app():
    """Create and configure the Gradio interface."""
    with gr.Blocks(title="Podcastfy Demo", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 🎙️ Podcastfy Demo
            Transform text or web content into AI-generated podcasts
            """
        )
        
        with gr.Row():
            # Left Column - Settings
            with gr.Column(scale=3):
                with gr.Tabs():
                    # Input Tab
                    with gr.Tab("📝 Input"):
                        input_components = create_input_components()
                    
                    # Style Tab
                    with gr.Tab("🎨 Style"):
                        style_components = create_style_components()
                    
                    # Voice Tab
                    with gr.Tab("🎤 Voice"):
                        voice_components = create_voice_components(format_type=style_components['format_type'].value)
                    
                    # Length Tab (renamed from Longform)
                    with gr.Tab("⏱️ Length"):
                        longform_components = create_longform_components()
                
                # Generate Buttons
                with gr.Row():
                    generate_btn = gr.Button("🎙️ Generate Podcast", size="lg", variant="primary")
                    generate_transcript_btn = gr.Button("📝 Generate Transcript", size="lg", variant="secondary")
                
                # Progress Tracking
                progress_components = create_progress_components()
            
            # Right Column - Output
            with gr.Column(scale=2):
                audio_output = gr.Audio(
                    label="Generated Podcast",
                    show_label=True
                )
                transcript_output = gr.Textbox(
                    label="Generated Transcript",
                    lines=15,
                    interactive=False,
                    show_label=True
                )
        
        # Event handlers
        def generate_transcript_interface(*args):
            """Interface for transcript-only generation."""
            # Extract arguments
            (text_input, url_input, file_input, directory_input, recursive, file_types,
             format_type, style, creativity, podcast_name, podcast_tagline,
             dialogue_structure, role1, role2, engagement, user_instructions,
             longform_enabled, chunk_size, num_chunks) = args
            
            # Initialize progress tracking
            yield None, update_generation_progress(0, None, 0)[0]
            
            try:
                # Input validation - check if any input is provided
                if not any([text_input, url_input, file_input, directory_input]):
                    yield "Please provide input via text, URL, file upload, or directory path.", update_generation_progress(0, "No input provided", 0)[0]
                    return

                # Process multiple URLs if provided
                urls = None
                if url_input:
                    url_file = process_multiple_urls(url_input)
                    if url_file:
                        with open(url_file, 'r') as f:
                            urls = [line.strip() for line in f if line.strip()]
                        os.unlink(url_file)  # Clean up temporary file
                
                # Create conversation config dictionary
                config = {
                    'format_type': format_type,
                    'creativity': creativity
                }
                
                # Add optional fields if they exist
                if style:
                    config['conversation_style'] = [style]  # Single style as list for compatibility
                if podcast_name:
                    config['podcast_name'] = podcast_name
                if podcast_tagline:
                    config['podcast_tagline'] = podcast_tagline
                if dialogue_structure:
                    config['dialogue_structure'] = [dialogue_structure]  # Single structure as list
                if role1:
                    config['roles_person1'] = role1
                if role2:  # Allow role2 to be passed to LLM even for monologue
                    config['roles_person2'] = role2  # LLM will handle it based on format
                if engagement:
                    config['engagement_techniques'] = engagement
                if user_instructions:
                    config['user_instructions'] = user_instructions

                if longform_enabled:
                    config['chunk_settings'] = {
                        'max_num_chunks': num_chunks,
                        'min_chunk_size': chunk_size
                    }
                
                # Validate style configuration
                validate_style_config(format_type, config)
                
                # Processing input (Stage 1)
                yield None, update_generation_progress(1, None, 50)[0]
                
                # Generate transcript
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
                elif text_input:
                    transcript_file = generate_podcast(
                        text=text_input,
                        transcript_only=True,
                        longform=longform_enabled,
                        conversation_config=config
                    )
                elif file_input:
                    # Handle multiple files
                    image_paths = []
                    text_content = []
                    file_urls = []
                    
                    for file_path in file_input:
                        if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                            image_paths.append(file_path)
                        elif file_path.lower().endswith('.pdf'):
                            file_urls.append(file_path)  # PDF extractor handles this
                        elif file_path.lower().endswith('.txt'):
                            with open(file_path, 'r') as f:
                                text_content.append(f.read())
                        else:
                            yield f"Unsupported file type: {file_path}", update_generation_progress(0, "Invalid file type", 0)[0]
                            return
                    
                    # Generate transcript with all inputs
                    transcript_file = generate_podcast(
                        text="\n\n".join(text_content) if text_content else None,
                        urls=file_urls if file_urls else None,
                        image_paths=image_paths if image_paths else None,
                        transcript_only=True,
                        longform=longform_enabled,
                        conversation_config=config
                    )
                elif urls:  # From processed URL input
                    transcript_file = generate_podcast(
                        urls=urls,
                        transcript_only=True,
                        longform=longform_enabled,
                        conversation_config=config
                    )
                
                # Read generated transcript
                with open(transcript_file, 'r') as f:
                    transcript = f.read()
                
                # Complete (Stage 2)
                yield transcript, update_generation_progress(2, None, 100)[0]
                
            except Exception as e:
                yield f"Error: {str(e)}", update_generation_progress(0, "Generation failed", 0)[0]

        def generate_podcast_interface(*args):
            """Main interface for podcast generation."""
            # Extract arguments
            (text_input, url_input, file_input, directory_input, recursive, file_types,
             format_type, style, creativity, podcast_name, podcast_tagline,
             dialogue_structure, role1, role2, engagement, user_instructions,
             tts_model, voice1, voice2, output_language,
             longform_enabled, chunk_size, num_chunks) = args
            
            # Initialize progress tracking
            yield None, None, update_generation_progress(0, None, 0)[0]
            
            try:
                # Input validation - check if any input is provided
                if not any([text_input, url_input, file_input, directory_input]):
                    yield None, "Please provide input via text, URL, file upload, or directory path.", update_generation_progress(0, "No input provided", 0)[0]
                    return

                # Process multiple URLs if provided
                urls = None
                if url_input:
                    url_file = process_multiple_urls(url_input)
                    if url_file:
                        with open(url_file, 'r') as f:
                            urls = [line.strip() for line in f if line.strip()]
                        os.unlink(url_file)  # Clean up temporary file
                
                # Add run metadata
                run_metadata = {
                    "input_type": "file" if file_input else "text" if text_input else "url",
                    "format_type": format_type,
                    "longform_enabled": longform_enabled,
                    "tts_model": tts_model,
                    "output_language": output_language,
                    "has_directory_input": bool(directory_input),
                    "has_recursive_directory": bool(directory_input and recursive),
                    "has_file_types": bool(file_types and "All Files" not in file_types),
                    "has_urls": bool(url_input),
                    "has_text": bool(text_input),
                    "has_style": bool(style),
                    "has_podcast_name": bool(podcast_name),
                    "has_podcast_tagline": bool(podcast_tagline),
                    "has_dialogue_structure": bool(dialogue_structure),
                    "has_roles": bool(role1 or role2),
                    "has_engagement": bool(engagement),
                    "has_user_instructions": bool(user_instructions),
                    "has_voice_config": bool(voice1 or voice2),
                    "chunk_settings": {
                        "enabled": longform_enabled,
                        "chunk_size": chunk_size if longform_enabled else None,
                        "num_chunks": num_chunks if longform_enabled else None
                    }
                }
                
                # Create conversation config dictionary
                config = {
                    'format_type': format_type,
                    'creativity': creativity
                }
                
                # Add optional fields if they exist
                if style:
                    config['conversation_style'] = [style]  # Single style as list for compatibility
                if podcast_name:
                    config['podcast_name'] = podcast_name
                if podcast_tagline:
                    config['podcast_tagline'] = podcast_tagline
                if dialogue_structure:
                    config['dialogue_structure'] = [dialogue_structure]  # Single structure as list
                if role1:
                    config['roles_person1'] = role1
                if role2:  # Allow role2 to be passed to LLM even for monologue
                    config['roles_person2'] = role2  # LLM will handle it based on format
                if engagement:
                    config['engagement_techniques'] = engagement
                if user_instructions:
                    config['user_instructions'] = user_instructions
                if output_language:
                    config['output_language'] = output_language

                if longform_enabled:
                    config['chunk_settings'] = {
                        'max_num_chunks': num_chunks,
                        'min_chunk_size': chunk_size
                    }
                
                # Validate style configuration
                validate_style_config(format_type, config)
                
                # Processing input (Stage 1)
                yield None, None, update_generation_progress(1, None, 25)[0]
                
                # Generate podcast
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
                elif text_input:
                    transcript_file = generate_podcast(
                        text=text_input,
                        transcript_only=True,
                        longform=longform_enabled,
                        conversation_config=config
                    )
                elif file_input:
                    # Handle multiple files
                    image_paths = []
                    text_content = []
                    file_urls = []
                    
                    for file_path in file_input:
                        if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                            image_paths.append(file_path)
                        elif file_path.lower().endswith('.pdf'):
                            file_urls.append(file_path)  # PDF extractor handles this
                        elif file_path.lower().endswith('.txt'):
                            with open(file_path, 'r') as f:
                                text_content.append(f.read())
                        else:
                            yield None, f"Unsupported file type: {file_path}", update_generation_progress(0, "Invalid file type", 0)[0]
                            return
                    
                    # Generate podcast with all inputs
                    transcript_file = generate_podcast(
                        text="\n\n".join(text_content) if text_content else None,
                        urls=file_urls if file_urls else None,
                        image_paths=image_paths if image_paths else None,
                        transcript_only=True,
                        longform=longform_enabled,
                        conversation_config=config
                    )
                elif urls:  # From processed URL input
                    transcript_file = generate_podcast(
                        urls=urls,
                        transcript_only=True,
                        longform=longform_enabled,
                        conversation_config=config
                    )
                
                # Read generated transcript
                with open(transcript_file, 'r') as f:
                    transcript = f.read()
                
                # Generating transcript (Stage 2)
                yield None, None, update_generation_progress(2, None, 50)[0]
                
                # Starting TTS (Stage 3)
                yield None, None, update_generation_progress(3, None, 60)[0]
                
                # Processing TTS Chunks (Stage 4)
                yield None, None, update_generation_progress(4, None, 70)[0]
                
                # Combining Audio (Stage 5)
                yield None, None, update_generation_progress(5, None, 80)[0]
                audio_file = generate_audio(transcript, tts_model, voice1, voice2, format_type)
                if not audio_file:
                    yield None, "Failed to generate audio", update_generation_progress(0, "Audio generation failed", 0)[0]
                    return
                
                # Complete (Stage 6)
                yield audio_file, transcript, update_generation_progress(6, None, 100)[0]
                
            except Exception as e:
                # Add error metadata
                run_metadata["error"] = str(e)
                run_metadata["error_type"] = type(e).__name__
                yield None, f"Error: {str(e)}", update_generation_progress(0, "Generation failed", 0)[0]
        
        # Style events
        style_components['style'].change(
            fn=update_style_fields,
            inputs=[style_components['style'], style_components['format_type']],
            outputs=[
                style_components['role1'],
                style_components['role2'],
                style_components['engagement']
            ]
        )
        
        # Longform events
        chunk_config = longform_components['chunk_config']
        chunk_config.change(
            fn=update_chunk_sliders,
            inputs=[chunk_config],
            outputs=[
                longform_components['chunk_size'],
                longform_components['num_chunks']
            ]
        )
        
        longform_components['longform_enabled'].change(
            fn=toggle_longform_controls,
            inputs=[longform_components['longform_enabled']],
            outputs=[
                longform_components['chunk_config'],
                longform_components['chunk_size'],
                longform_components['num_chunks']
            ]
        )
        
        # Voice events
        voice_components['tts_model'].change(
            fn=update_voice_choices,
            inputs=[
                voice_components['tts_model'],
                style_components['format_type']
            ],
            outputs=[
                voice_components['voice1'],
                voice_components['voice2'],
                voice_components['sample_btn'],
                voice_components['sample_audio']
            ]
        )
        
        voice_components['sample_btn'].click(
            fn=sample_voice,
            inputs=[
                voice_components['voice1'],
                voice_components['voice2'],
                voice_components['tts_model'],
                style_components['format_type']
            ],
            outputs=[voice_components['sample_audio']]
        )

        # Update voice components when format changes
        style_components['format_type'].change(
            fn=update_voice_choices,
            inputs=[
                voice_components['tts_model'],
                style_components['format_type']
            ],
            outputs=[
                voice_components['voice1'],
                voice_components['voice2'],
                voice_components['sample_btn'],
                voice_components['sample_audio']
            ]
        )
        
        # Generate events
        generate_transcript_btn.click(
            fn=generate_transcript_interface,
            inputs=[
                input_components['text_input'],
                input_components['url_input'],
                input_components['file_input'],
                input_components['directory_input'],
                input_components['recursive'],
                input_components['file_types'],
                style_components['format_type'],
                style_components['style'],
                style_components['creativity'],
                style_components['podcast_name'],
                style_components['podcast_tagline'],
                style_components['dialogue_structure'],
                style_components['role1'],
                style_components['role2'],
                style_components['engagement'],
                style_components['user_instructions'],
                longform_components['longform_enabled'],
                longform_components['chunk_size'],
                longform_components['num_chunks']
            ],
            outputs=[
                transcript_output,
                progress_components['stages']
            ]
        )

        generate_btn.click(
            fn=generate_podcast_interface,
            inputs=[
                input_components['text_input'],
                input_components['url_input'],
                input_components['file_input'],
                input_components['directory_input'],
                input_components['recursive'],
                input_components['file_types'],
                style_components['format_type'],
                style_components['style'],
                style_components['creativity'],
                style_components['podcast_name'],
                style_components['podcast_tagline'],
                style_components['dialogue_structure'],
                style_components['role1'],
                style_components['role2'],
                style_components['engagement'],
                style_components['user_instructions'],
                voice_components['tts_model'],
                voice_components['voice1'],
                voice_components['voice2'],
                voice_components['output_language'],
                longform_components['longform_enabled'],
                longform_components['chunk_size'],
                longform_components['num_chunks']
            ],
            outputs=[
                audio_output,
                transcript_output,
                progress_components['stages']  # Now contains both progress and status
            ]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_app()
    demo.launch(server_name="0.0.0.0")
