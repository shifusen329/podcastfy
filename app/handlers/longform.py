"""Event handlers for longform components."""

import gradio as gr
from ..components.longform import update_chunk_sliders as update_sliders
from ..config.settings import CHUNK_CONFIGS

def update_chunk_sliders(choice):
    """Handle chunk slider updates when configuration is changed."""
    try:
        # Extract preset name from choice
        preset = choice.split(" (")[0]
        # Add run metadata
        run_metadata = {
            "preset": preset,
            "chunk_config": CHUNK_CONFIGS.get(preset, CHUNK_CONFIGS['default'])
        }
        return update_sliders(choice)
    except Exception as e:
        # Add error metadata
        run_metadata["error"] = str(e)
        run_metadata["error_type"] = type(e).__name__
        print(f"Error updating chunk sliders: {str(e)}")
        return None

def validate_longform_settings(longform_enabled, chunk_size, num_chunks, text_input=None, url_input=None):
    """Validate longform settings."""
    # Add run metadata
    run_metadata = {
        "longform_enabled": longform_enabled,
        "chunk_size": chunk_size,
        "num_chunks": num_chunks
    }
    
    if not longform_enabled:
        return True, "Longform mode disabled"
    
    errors = []
    
    # Validate chunk settings
    if chunk_size < CHUNK_CONFIGS['default']['min_chunk_size']:
        errors.append(f"Chunk size must be at least {CHUNK_CONFIGS['default']['min_chunk_size']}")
    if num_chunks < CHUNK_CONFIGS['default']['max_num_chunks']:
        errors.append(f"Number of chunks must be at least {CHUNK_CONFIGS['default']['max_num_chunks']}")
    
    # Add validation result to metadata
    run_metadata["valid"] = len(errors) == 0
    if errors:
        run_metadata["errors"] = errors
    
    return len(errors) == 0, "\n".join(errors) if errors else "Valid"

def toggle_longform_controls(enabled):
    """Handle visibility of longform controls."""
    # Add run metadata
    run_metadata = {
        "enabled": enabled
    }
    
    try:
        return [
            gr.Radio(visible=enabled),  # chunk_config
            gr.Slider(visible=enabled),  # chunk_size
            gr.Slider(visible=enabled)   # num_chunks
        ]
    except Exception as e:
        # Add error metadata
        run_metadata["error"] = str(e)
        run_metadata["error_type"] = type(e).__name__
        print(f"Error toggling longform controls: {str(e)}")
        return [
            gr.Radio(visible=False),
            gr.Slider(visible=False),
            gr.Slider(visible=False)
        ]
