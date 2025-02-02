"""Main Gradio interface for Podcastfy."""

import gradio as gr
import os
from podcastfy.client import generate_podcast
from langsmith import traceable

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
                
                # Progress Tracking
                progress_components = create_progress_components()
                
                # Generate Button
                with gr.Row():
                    generate_btn = gr.Button("🎙️ Generate Podcast", size="lg", variant="primary")
            
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
        @traceable(run_name="generate_podcast", tags=["podcastfy"])
        def generate_podcast_interface(*args):
            """Main interface for podcast generation."""
            # Extract arguments
            (text_input, url_input, format_type, style, creativity, podcast_name, podcast_tagline,
             dialogue_structure, role1, role2, engagement, user_instructions,
             tts_model, voice1, voice2, output_language,
             longform_enabled, chunk_size, num_chunks) = args
            
            # Initialize progress tracking
            yield None, None, gr.Slider(value=0), gr.Label(value="Starting podcast generation...")
            
            try:
                # Input validation - only check if any input is provided
                if not text_input and not url_input:
                    yield None, "Please provide either text or URL input.", gr.Slider(value=0), gr.Label(value="Error: No input provided")
                    return
                
                # Add run metadata
                run_metadata = {
                    "input_type": "text" if text_input else "url",
                    "format_type": format_type,
                    "longform_enabled": longform_enabled,
                    "tts_model": tts_model,
                    "output_language": output_language
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
                
                # Generate transcript
                yield None, None, gr.Slider(value=25), gr.Label(value="Generating transcript...")
                
                # Generate podcast
                if text_input:
                    # Check if input is a directory path
                    if is_text_directory(text_input):
                        try:
                            # Combine all text files into one string
                            combined_text, was_truncated = combine_directory_texts(text_input)
                            if was_truncated:
                                yield None, None, gr.Slider(value=25), gr.Label(value="Warning: Content too large, using most recent files up to 20MB...")
                            transcript_file = generate_podcast(
                                text=combined_text,  # Pass combined text directly
                                transcript_only=True,
                                longform=longform_enabled,
                                conversation_config=config
                            )
                        except ValueError as e:
                            yield None, f"Error processing directory: {str(e)}", gr.Slider(value=0), gr.Label(value="Error: Directory processing failed")
                            return
                    else:
                        # Regular text input
                        transcript_file = generate_podcast(
                            text=text_input,
                            transcript_only=True,
                            longform=longform_enabled,
                            conversation_config=config
                        )
                else:  # url_input
                    # Check if input is a directory path
                    if is_text_directory(url_input):
                        try:
                            # Combine all text files into one string
                            combined_text, was_truncated = combine_directory_texts(url_input)
                            if was_truncated:
                                yield None, None, gr.Slider(value=25), gr.Label(value="Warning: Content too large, using most recent files up to 20MB...")
                            transcript_file = generate_podcast(
                                text=combined_text,  # Pass combined text directly
                                transcript_only=True,
                                longform=longform_enabled,
                                conversation_config=config
                            )
                        except ValueError as e:
                            yield None, f"Error processing directory: {str(e)}", gr.Slider(value=0), gr.Label(value="Error: Directory processing failed")
                            return
                    else:
                        # Regular URL input
                        transcript_file = generate_podcast(
                            urls=[url_input],
                            transcript_only=True,
                            longform=longform_enabled,
                            conversation_config=config
                        )
                
                # Read generated transcript
                with open(transcript_file, 'r') as f:
                    transcript = f.read()
                
                yield None, None, gr.Slider(value=50), gr.Label(value="Transcript generation complete")
                
                # Generate audio
                yield None, None, gr.Slider(value=75), gr.Label(value="Generating audio...")
                audio_file = generate_audio(transcript, tts_model, voice1, voice2, format_type)
                if not audio_file:
                    yield None, "Failed to generate audio", gr.Slider(value=0), gr.Label(value="Error: Audio generation failed")
                    return
                
                # Complete
                yield audio_file, transcript, gr.Slider(value=100), gr.Label(value="Podcast generation complete!")
                
            except Exception as e:
                # Add error metadata
                run_metadata["error"] = str(e)
                run_metadata["error_type"] = type(e).__name__
                yield None, f"Error: {str(e)}", gr.Slider(value=0), gr.Label(value=f"Error: Generation failed")
        
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
        generate_btn.click(
            fn=generate_podcast_interface,
            inputs=[
                input_components['text_input'],
                input_components['url_input'],
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
                progress_components['bar'],
                progress_components['status']
            ]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_app()
    demo.launch(server_name="0.0.0.0")
