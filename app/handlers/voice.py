"""Event handlers for voice components."""

import os
import uuid
import tempfile
import gradio as gr
from langsmith import traceable
from podcastfy.text_to_speech import TextToSpeech
import sys
sys.path.append("/home/administrator/podcastfy-dev")  # Add root to path
from novel_ai_tts import NovelAITTS
from kokoro_tts import KokoroTTS
from podcastfy.tts.providers.openai import OpenAITTS
from podcastfy.tts.providers.gemini import GeminiTTS
from ..components.voice import get_model_voices, create_sample_text
from ..config.settings import AUDIO_DIR

def update_voice_choices(tts_model, format_type="conversation"):
    """Update voice dropdown choices based on selected TTS model and format."""
    voices = get_model_voices(tts_model)
    if not voices:  # No voices available
        return [
            gr.Dropdown(visible=False),
            gr.Dropdown(visible=False),
            gr.Button(visible=False),
            gr.Audio(visible=False)
        ]
    
    # Get default voices based on provider
    if tts_model == "kokoro":
        default_voice1, default_voice2 = "af", "af_bella"
    elif tts_model == "novel-ai":
        default_voice1, default_voice2 = "Ligeia", "Aini"
    elif tts_model == "openai":
        default_voice1, default_voice2 = "echo", "alloy"
    elif tts_model == "gemini":
        default_voice1, default_voice2 = "en-US-Journey-D", "en-US-Journey-O"
    else:
        default_voice1 = voices[0]
        default_voice2 = voices[1] if len(voices) > 1 else voices[0]
    
    # Voice 1 label changes based on format
    voice1_label = "Narrator" if format_type == "monologue" else "Voice 1 (Person1)"
    voice1 = gr.Dropdown(
        choices=voices,
        value=default_voice1,
        label=voice1_label,
        visible=True,
        interactive=True
    )
    
    # Voice 2 only visible for conversation format
    voice2 = gr.Dropdown(
        choices=voices,
        value=default_voice2,
        label="Voice 2 (Person2)",
        visible=format_type == "conversation",
        interactive=True
    )
    
    sample_btn = gr.Button(value="🔊 Sample Voices", visible=True)
    sample_audio = gr.Audio(visible=True)
    
    return [voice1, voice2, sample_btn, sample_audio]

@traceable(run_name="sample_voice", tags=["podcastfy", "voice-sample"])
def sample_voice(voice1, voice2, tts_model, format_type="conversation"):
    """Generate a sample audio using selected voices."""
    try:
        # Get sample text based on format
        sample_text = create_sample_text(format_type)
        
        # Add run metadata
        run_metadata = {
            "tts_model": tts_model,
            "format_type": format_type,
            "voice1": voice1,
            "voice2": voice2
        }
        
        # Only use voice2 for conversation format
        voice2_param = voice2 if format_type == "conversation" else None
        
        # Initialize TTS provider based on model
        if tts_model == "novel-ai":
            tts_provider = NovelAITTS()
            model = "novel-ai-tts-1"
        elif tts_model == "kokoro":
            tts_provider = KokoroTTS()
            model = "kokoro"
        elif tts_model == "openai":
            tts_provider = OpenAITTS()
            model = "tts-1-hd"
        elif tts_model == "gemini":
            tts_provider = GeminiTTS()
            model = None  # Uses default model
        elif tts_model == "geminimulti":
            from podcastfy.tts.providers.geminimulti import GeminiMultiTTS
            tts_provider = GeminiMultiTTS()
            model = "en-US-Studio-MultiSpeaker"
        else:
            raise ValueError(f"Unsupported TTS model: {tts_model}")
        
        # Generate sample audio
        audio_content = tts_provider.generate_audio(
            text=sample_text,
            voice=voice1,
            model=model,
            voice2=voice2_param
        )
            
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            tmp.write(audio_content)
            return tmp.name
            
    except Exception as e:
        # Add error metadata
        run_metadata["error"] = str(e)
        run_metadata["error_type"] = type(e).__name__
        print(f"Error sampling voice: {str(e)}")
        return None

@traceable(run_name="generate_audio", tags=["podcastfy", "audio-generation"])
def generate_audio(transcript, tts_model, voice1=None, voice2=None, format_type="conversation"):
    """Generate audio from transcript using specified TTS model and voices."""
    try:
        # Add run metadata
        run_metadata = {
            "tts_model": tts_model,
            "format_type": format_type,
            "voice1": voice1,
            "voice2": voice2,
            "transcript_length": len(transcript)
        }
        
        # Get model name based on provider
        if tts_model == "novel-ai":
            model = "novel-ai-tts-1"
        elif tts_model == "kokoro":
            model = "kokoro"
        elif tts_model == "openai":
            model = "tts-1-hd"
        elif tts_model == "gemini":
            model = None  # Uses default model
        elif tts_model == "geminimulti":
            model = "en-US-Studio-MultiSpeaker"
        else:
            raise ValueError(f"Unsupported TTS model: {tts_model}")

        # Create conversation config with format type, voices and model
        conversation_config = {
            "format_type": format_type,
            "text_to_speech": {
                "default_voices": {
                    "question": voice1,
                    "answer": voice2
                },
                "default_model": model
            }
        }
        
        # Initialize TTS with config
        text_to_speech = TextToSpeech(
            model=tts_model,
            conversation_config=conversation_config
        )
        
        # Generate audio file
        random_filename = f"podcast_{uuid.uuid4().hex}.mp3"
        audio_file = os.path.join(AUDIO_DIR, random_filename)
        os.makedirs(AUDIO_DIR, exist_ok=True)
        
        print("\nStarting TTS generation...")
        # Convert transcript to speech
        text_to_speech.convert_to_speech(transcript, audio_file)
        print("TTS generation complete!")
        return audio_file
            
    except Exception as e:
        # Add error metadata
        run_metadata["error"] = str(e)
        run_metadata["error_type"] = type(e).__name__
        print(f"Error generating audio: {str(e)}")
        return None

@traceable(run_name="validate_voice_settings", tags=["podcastfy", "validation"])
def validate_voice_settings(tts_model, format_type="conversation", voice1=None, voice2=None):
    """Validate voice settings based on selected TTS model and format."""
    # Add run metadata
    run_metadata = {
        "tts_model": tts_model,
        "format_type": format_type,
        "voice1": voice1,
        "voice2": voice2
    }
    
    # Get available voices for the model
    voices = get_model_voices(tts_model)
    if not voices:
        return True, "Using default TTS model"
    
    errors = []
    
    # Validate voice1
    if not voice1:
        voice1_label = "Narrator" if format_type == "monologue" else "Voice 1"
        errors.append(f"{voice1_label} must be selected")
    elif voice1 not in voices:
        errors.append(f"Invalid {voice1_label}: {voice1}")
    
    # Only validate voice2 for conversation format
    if format_type == "conversation":
        if not voice2:
            errors.append("Voice 2 must be selected")
        elif voice2 not in voices:
            errors.append(f"Invalid Voice 2: {voice2}")
        elif voice1 == voice2:
            errors.append("Voice 1 and Voice 2 must be different")
    
    # Add validation result to metadata
    run_metadata["valid"] = len(errors) == 0
    if errors:
        run_metadata["errors"] = errors
    
    return len(errors) == 0, "\n".join(errors) if errors else "Valid"
