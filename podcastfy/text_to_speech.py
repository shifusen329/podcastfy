"""
Text-to-Speech Module for converting text into speech using various providers.

This module provides functionality to convert text into speech using various TTS models.
It supports ElevenLabs, Google, OpenAI and Edge TTS services and handles the conversion process,
including cleaning of input text and merging of audio files.
"""

import io
import logging
import os
import re
import tempfile
from typing import List, Tuple, Optional, Dict, Any
from pydub import AudioSegment

from .tts.factory import TTSProviderFactory
from .utils.config import load_config
from .utils.config_conversation import load_conversation_config

logger = logging.getLogger(__name__)


class TextToSpeech:
    def __init__(
        self,
        model: str = None,
        api_key: Optional[str] = None,
        conversation_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the TextToSpeech class.

        Args:
                        model (str): The model to use for text-to-speech conversion.
                                                Options are 'elevenlabs', 'gemini', 'openai', 'edge' or 'geminimulti'. Defaults to 'openai'.
                        api_key (Optional[str]): API key for the selected text-to-speech service.
                        conversation_config (Optional[Dict]): Configuration for conversation settings.
        """
        self.config = load_config()
        self.conversation_config = load_conversation_config(conversation_config)
        self.tts_config = self.conversation_config.get("text_to_speech", {})
        self.format_type = self.conversation_config.get("format_type", "conversation")

        # Get API key from config if not provided
        if not api_key:
            api_key = getattr(self.config, f"{model.upper().replace('MULTI', '')}_API_KEY", None)

        # Initialize provider using factory
        self.provider = TTSProviderFactory.create(
            provider_name=model, api_key=api_key, model=model
        )

        # Setup directories and config
        self._setup_directories()
        self.audio_format = self.tts_config.get("audio_format", "mp3")
        self.ending_message = self.tts_config.get("ending_message", "")

    def _get_provider_config(self) -> Dict[str, Any]:
        """Get provider-specific configuration."""
        # Get provider name in lowercase without 'TTS' suffix
        provider_name = self.provider.__class__.__name__.lower().replace("tts", "")
        
        # Get default voices from the config passed in
        voices = self.tts_config.get("default_voices", {})
        
        # Get model from provider config or default
        model = self.tts_config.get("default_model")
        
        provider_config = {
            "default_voices": voices,
            "model": model
        }
        
        logger.debug(f"Using provider config: {provider_config}")
        return provider_config

    def convert_to_speech(self, text: str, output_file: str) -> None:
        """
        Convert input text to speech and save as an audio file.

        Args:
                text (str): Input text to convert to speech.
                output_file (str): Path to save the output audio file.

        Raises:
            ValueError: If the input text is not properly formatted
        """
        cleaned_text = text

        try:
            if (
                "multi" in self.provider.model.lower()
            ):  # refactor: We should have instead MultiSpeakerTTS and SingleSpeakerTTS classes
                provider_config = self._get_provider_config()
                voice = provider_config.get("default_voices", {}).get("question")
                voice2 = provider_config.get("default_voices", {}).get("answer")
                model = provider_config.get("model")
                audio_data_list = self.provider.generate_audio(
                    cleaned_text,
                    voice=voice,
                    model=model,
                    voice2=voice2 if self.format_type == "conversation" else None,
                    ending_message=self.ending_message,
                )

                try:
                    # First verify we have data
                    if not audio_data_list:
                        raise ValueError("No audio data chunks provided")

                    logger.info(f"Starting audio processing with {len(audio_data_list)} chunks")
                    combined = AudioSegment.empty()
                    
                    for i, chunk in enumerate(audio_data_list):
                        segment = AudioSegment.from_file(io.BytesIO(chunk))
                        logger.info(f"################### Loaded chunk {i}, duration: {len(segment)}ms")
                        
                        combined += segment
                    
                    # Export with high quality settings
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                    combined.export(
                        output_file, 
                        format=self.audio_format,
                        codec="libmp3lame",
                        bitrate="320k"
                    )
                    
                except Exception as e:
                    logger.error(f"Error during audio processing: {str(e)}")
                    raise
            else:
                # For single speaker providers
                provider_config = self._get_provider_config()
                voice = provider_config.get("default_voices", {}).get("question")
                voice2 = provider_config.get("default_voices", {}).get("answer")
                model = provider_config.get("model")
                
                # Generate audio with voice2 for conversation format
                audio_data = self.provider.generate_audio(
                    cleaned_text,
                    voice=voice,
                    model=model,
                    voice2=voice2 if self.format_type == "conversation" else None
                )
                
                # Save audio data directly
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, "wb") as f:
                    f.write(audio_data)
                logger.info(f"Audio saved to {output_file}")

        except Exception as e:
            logger.error(f"Error converting text to speech: {str(e)}")
            raise

    def _setup_directories(self) -> None:
        """Setup required directories for audio processing."""
        self.output_directories = self.tts_config.get("output_directories", {})
        temp_dir = self.tts_config.get("temp_audio_dir", "data/audio/tmp/").rstrip("/").split("/")
        self.temp_audio_dir = os.path.join(*temp_dir)
        base_dir = os.path.abspath(os.path.dirname(__file__))
        self.temp_audio_dir = os.path.join(base_dir, self.temp_audio_dir)

        os.makedirs(self.temp_audio_dir, exist_ok=True)

        # Create directories if they don't exist
        for dir_path in [
            self.output_directories.get("transcripts"),
            self.output_directories.get("audio"),
            self.temp_audio_dir,
        ]:
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)


def main(seed: int = 42) -> None:
    """
    Main function to test the TextToSpeech class.

    Args:
            seed (int): Random seed for reproducibility. Defaults to 42.
    """
    try:
        # Load configuration
        config = load_config()

        # Override default TTS model to use edge for tests
        test_config = {"text_to_speech": {"default_tts_model": "edge"}}

        # Read input text from file
        with open(
            "tests/data/transcript_336aa9f955cd4019bc1287379a5a2820.txt", "r"
        ) as file:
            input_text = file.read()

        # Test ElevenLabs
        tts_elevenlabs = TextToSpeech(model="elevenlabs")
        elevenlabs_output_file = "tests/data/response_elevenlabs.mp3"
        tts_elevenlabs.convert_to_speech(input_text, elevenlabs_output_file)
        logger.info(
            f"ElevenLabs TTS completed. Output saved to {elevenlabs_output_file}"
        )

        # Test OpenAI
        tts_openai = TextToSpeech(model="openai")
        openai_output_file = "tests/data/response_openai.mp3"
        tts_openai.convert_to_speech(input_text, openai_output_file)
        logger.info(f"OpenAI TTS completed. Output saved to {openai_output_file}")

        # Test Edge
        tts_edge = TextToSpeech(model="edge")
        edge_output_file = "tests/data/response_edge.mp3"
        tts_edge.convert_to_speech(input_text, edge_output_file)
        logger.info(f"Edge TTS completed. Output saved to {edge_output_file}")

    except Exception as e:
        logger.error(f"An error occurred during text-to-speech conversion: {str(e)}")
        raise


if __name__ == "__main__":
    main(seed=42)
