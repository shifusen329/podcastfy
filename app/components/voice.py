"""Voice components for the Podcastfy UI."""

import gradio as gr
import requests
import json
import tempfile
import openai
from google.cloud import texttospeech_v1beta1
from ..config.settings import TTS_MODELS, LANGUAGES
import logging

logger = logging.getLogger(__name__)

def get_model_voices(model):
    """Get available voices for a specific TTS model."""
    if model == "kokoro":
        try:
            response = requests.get("http://localhost:8880/v1/audio/voices")
            logger.debug(f"Voice API Response: {response.text}")
            text = response.text.replace('""', '","')
            voices = json.loads(text)
            if isinstance(voices, dict) and 'voices' in voices:
                return voices['voices']
            else:
                logger.warning(f"Unexpected voice data format: {voices}")
                return ["af"]
        except Exception as e:
            logger.error(f"Error fetching kokoro voices: {str(e)}")
            return ["af"]
    elif model == "novel-ai":
        return [
            "Ligeia", "Aini", "Orea", "Claea", "Lim", "Aurae", 
            "Naia", "Aulon", "Elei", "Ogma", "Raid", "Pega", "Lam"
        ]
    elif model == "openai":
        # OpenAI has fixed set of voices
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    elif model == "gemini":
        try:
            from podcastfy.tts.providers.gemini import GeminiTTS
            provider = GeminiTTS()
            voices = provider.get_available_voices()
            return voices if voices else ["en-US-Journey-D", "en-US-Journey-O"]  # Fallback to defaults
        except Exception as e:
            logger.error(f"Error fetching Gemini voices: {str(e)}")
            return ["en-US-Journey-D", "en-US-Journey-O"]  # Fallback to defaults
    elif model == "geminimulti":
        # Studio Multi-Speaker voices
        return ["R", "S"]  # Fixed set of speakers for multi-speaker model
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
            # Get initial voices for OpenAI (default provider)
            openai_voices = get_model_voices("openai")
            voice1 = gr.Dropdown(
                choices=openai_voices,
                value="echo",  # Default OpenAI voice
                label=voice1_label,
                visible=True,
                interactive=True
            )
            # Voice 2 only visible for conversation format
            voice2 = gr.Dropdown(
                choices=openai_voices,
                value="alloy",  # Different default for second voice
                label="Voice 2 (Person2)",
                visible=format_type == "conversation",
                interactive=True
            )
        with gr.Row():
            sample_btn = gr.Button("🔊 Sample Voices", visible=True)
            sample_audio = gr.Audio(label="Voice Sample", visible=True)
        
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
