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
from ..components.voice import get_model_voices, create_sample_text
from ..config.settings import AUDIO_DIR

def update_voice_choices(tts_model, format_type="conversation"):
    """Update voice dropdown choices based on selected TTS model and format."""
    if tts_model in ["kokoro", "novel-ai"]:
        voices = get_model_voices(tts_model)
        default_voice1 = "af" if tts_model == "kokoro" else "Ligeia"
        default_voice2 = "af_bella" if tts_model == "kokoro" else "Aini"
        
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
    
    # For other TTS models, hide voice selection
    return [
        gr.Dropdown(visible=False, value=None),
        gr.Dropdown(visible=False, value=None),
        gr.Button(visible=False),
        gr.Audio(visible=False)
    ]

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
        
        # Generate sample audio
        if tts_model == "novel-ai":
            tts_provider = NovelAITTS()
            audio_content = tts_provider.generate_audio(
                text=sample_text,
                voice=voice1,
                model="novel-ai-tts-1",
                voice2=voice2_param
            )
        else:  # kokoro
            tts_provider = KokoroTTS()
            audio_content = tts_provider.generate_audio(
                text=sample_text,
                voice=voice1,
                model="kokoro",
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
        
        # Create conversation config with format type and voices
        conversation_config = {
            "format_type": format_type,
            "text_to_speech": {
                "default_voices": {
                    "question": voice1,
                    "answer": voice2
                }
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
        
        # Convert transcript to speech
        text_to_speech.convert_to_speech(transcript, audio_file)
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
    
    if tts_model not in ["kokoro", "novel-ai"]:
        return True, "Using default TTS model"
    
    errors = []
    
    if not voice1:
        voice1_label = "Narrator" if format_type == "monologue" else "Voice 1"
        errors.append(f"{voice1_label} must be selected")
    
    # Only validate voice2 for conversation format
    if format_type == "conversation":
        if not voice2:
            errors.append("Voice 2 must be selected")
        if voice1 == voice2:
            errors.append("Voice 1 and Voice 2 must be different")
    
    # Add validation result to metadata
    run_metadata["valid"] = len(errors) == 0
    if errors:
        run_metadata["errors"] = errors
    
    return len(errors) == 0, "\n".join(errors) if errors else "Valid"
