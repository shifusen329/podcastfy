"""Longform components for the Podcastfy UI."""

import gradio as gr
from ..config.settings import CHUNK_CONFIGS

def create_longform_components():
    """Create components for longform settings."""
    with gr.Group():
        gr.Markdown("### Longform Settings")
        longform_enabled = gr.Checkbox(
            label="Enable Longform Mode",
            value=False,
            info="Generate longer podcasts from extensive content"
        )
        # Create choices with descriptions
        choices = [f"{preset} ({config['description']})" for preset, config in CHUNK_CONFIGS.items()]
        chunk_config = gr.Radio(
            choices=choices,
            value=f"default ({CHUNK_CONFIGS['default']['description']})",
            label="Length Preset",
            info="Select configuration based on desired podcast length",
            visible=False
        )
        with gr.Row():
            chunk_size = gr.Slider(
                minimum=600,
                maximum=2000,
                value=600,
                step=100,
                label="Minimum Chunk Size",
                visible=False
            )
            num_chunks = gr.Slider(
                minimum=7,
                maximum=15,
                value=7,
                step=1,
                label="Maximum Chunks",
                visible=False
            )
    
    return {
        'longform_enabled': longform_enabled,
        'chunk_config': chunk_config,
        'chunk_size': chunk_size,
        'num_chunks': num_chunks
    }

def update_chunk_sliders(choice):
    """Update chunk size and number sliders based on selected configuration."""
    # Extract preset name from choice (e.g., "default (15-20 min podcast)" -> "default")
    preset = choice.split(" (")[0]
    config = CHUNK_CONFIGS[preset]
    return [
        gr.Slider(value=config['min_chunk_size']),
        gr.Slider(value=config['max_num_chunks'])
    ]

def create_chunk_config(longform_enabled, chunk_size, num_chunks):
    """Create chunk configuration dictionary if longform is enabled."""
    if not longform_enabled:
        return {}
    
    return {
        'chunk_settings': {
            'max_num_chunks': num_chunks,
            'min_chunk_size': chunk_size
        }
    }
