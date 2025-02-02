"""Voice components for the Podcastfy UI."""

import gradio as gr
import requests
import json
import tempfile
from ..config.settings import TTS_MODELS, LANGUAGES

def get_model_voices(model):
    """Get available voices for a specific TTS model."""
    if model == "kokoro":
        try:
            response = requests.get("http://localhost:8880/v1/audio/voices")
            print(f"Voice API Response: {response.text}")  # Debug log
            text = response.text.replace('""', '","')
            voices = json.loads(text)
            if isinstance(voices, dict) and 'voices' in voices:
                return voices['voices']
            else:
                print(f"Unexpected voice data format: {voices}")
                return ["af"]
        except Exception as e:
            print(f"Error fetching kokoro voices: {str(e)}")
            return ["af"]
    elif model == "novel-ai":
        return [
            "Ligeia", "Aini", "Orea", "Claea", "Lim", "Aurae", 
            "Naia", "Aulon", "Elei", "Ogma", "Raid", "Pega", "Lam"
        ]
    return []

def create_voice_components(format_type="conversation"):
    """Create components for TTS voice settings."""
    with gr.Group():
        gr.Markdown("### TTS Settings")
        tts_model = gr.Dropdown(
            choices=TTS_MODELS,
            value="openai",
            label="TTS Model"
        )
        with gr.Row():
            # Voice 1 label changes based on format
            voice1_label = "Narrator" if format_type == "monologue" else "Voice 1 (Person1)"
            voice1 = gr.Dropdown(
                choices=[],  # Empty initially
                value=None,
                label=voice1_label,
                visible=False,
                interactive=True
            )
            # Voice 2 only visible for conversation format
            voice2 = gr.Dropdown(
                choices=[],  # Empty initially
                value=None,
                label="Voice 2 (Person2)",
                visible=False,
                interactive=True
            )
        with gr.Row():
            sample_btn = gr.Button("🔊 Sample Voices", visible=False)
            sample_audio = gr.Audio(label="Voice Sample", visible=False)
        
        output_language = gr.Dropdown(
            choices=LANGUAGES,
            value="English",
            label="Output Language"
        )
    
    return {
        'tts_model': tts_model,
        'voice1': voice1,
        'voice2': voice2,
        'sample_btn': sample_btn,
        'sample_audio': sample_audio,
        'output_language': output_language
    }

def create_sample_text(format_type="conversation"):
    """Create sample text for voice testing."""
    if format_type == "monologue":
        return "<Person1>This is a sample of the narrator's voice for the monologue format.</Person1>"
    else:
        return "<Person1>This is the first voice.</Person1>\n<Person2>And this is the second voice.</Person2>"
