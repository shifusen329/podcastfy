"""Google Cloud Text-to-Speech provider implementation for single speaker."""

from google.cloud import texttospeech_v1beta1
from typing import List, Tuple
from ..base import TTSProvider
import logging
import re

logger = logging.getLogger(__name__)

class GeminiTTS(TTSProvider):
    """Google Cloud Text-to-Speech provider for single speaker."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Google Cloud TTS provider.
        
        Args:
            api_key (str): Google Cloud API key
            model (str): Default voice model to use
        """
        self.model = model
        try:
            # Use Application Default Credentials
            self.client = texttospeech_v1beta1.TextToSpeechClient()
        except Exception as e:
            logger.error(f"Failed to initialize Google TTS client: {str(e)}")
            raise

    def get_available_voices(self):
        """Get available Journey voices from Google Cloud TTS."""
        try:
            response = self.client.list_voices()
            # Filter for Journey voices
            journey_voices = [
                voice.name for voice in response.voices 
                if "Journey" in voice.name
            ]
            return journey_voices
        except Exception as e:
            logger.error(f"Failed to fetch voices: {str(e)}")
            return []

    def generate_audio(self, text: str, voice: str = None, 
                      model: str = None, voice2: str = None, **kwargs) -> bytes:
        """
        Generate audio using Google Cloud TTS API.
        
        Args:
            text (str): Text to convert to speech
            voice (str): Voice ID/name to use (format: "{language-code}-{name}-{gender}")
            model (str): Optional model override
            voice2 (str): Optional second voice for conversation format
            
        Returns:
            bytes: Audio data
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If audio generation fails
        """
        self.validate_parameters(text, voice, model or self.model)
        
        try:
            # For conversation format, use different voices for Person1 and Person2
            if "<Person1>" in text and voice2:
                # Extract Person1 and Person2 content
                person1_pattern = r'<Person1>(.*?)</Person1>'
                person2_pattern = r'<Person2>(.*?)</Person2>'
                
                person1_matches = re.findall(person1_pattern, text, re.DOTALL)
                person2_matches = re.findall(person2_pattern, text, re.DOTALL)
                
                # Generate audio for Person1 content
                person1_audio = []
                for content in person1_matches:
                    synthesis_input = texttospeech_v1beta1.SynthesisInput(text=content.strip())
                    voice_params = texttospeech_v1beta1.VoiceSelectionParams(
                        language_code="-".join(voice.split("-")[:2]),
                        name=voice,
                    )
                    audio_config = texttospeech_v1beta1.AudioConfig(
                        audio_encoding=texttospeech_v1beta1.AudioEncoding.MP3
                    )
                    response = self.client.synthesize_speech(
                        input=synthesis_input,
                        voice=voice_params,
                        audio_config=audio_config
                    )
                    person1_audio.append(response.audio_content)
                
                # Generate audio for Person2 content
                person2_audio = []
                for content in person2_matches:
                    synthesis_input = texttospeech_v1beta1.SynthesisInput(text=content.strip())
                    voice_params = texttospeech_v1beta1.VoiceSelectionParams(
                        language_code="-".join(voice2.split("-")[:2]),
                        name=voice2,
                    )
                    audio_config = texttospeech_v1beta1.AudioConfig(
                        audio_encoding=texttospeech_v1beta1.AudioEncoding.MP3
                    )
                    response = self.client.synthesize_speech(
                        input=synthesis_input,
                        voice=voice_params,
                        audio_config=audio_config
                    )
                    person2_audio.append(response.audio_content)
                
                # Merge audio segments alternating between Person1 and Person2
                from pydub import AudioSegment
                import io
                
                combined = AudioSegment.empty()
                for p1, p2 in zip(person1_audio, person2_audio):
                    # Add Person1 audio
                    segment = AudioSegment.from_file(io.BytesIO(p1))
                    combined += segment
                    # Add Person2 audio
                    segment = AudioSegment.from_file(io.BytesIO(p2))
                    combined += segment
                
                # Handle any remaining Person1 audio
                if len(person1_audio) > len(person2_audio):
                    segment = AudioSegment.from_file(io.BytesIO(person1_audio[-1]))
                    combined += segment
                
                # Export combined audio
                output = io.BytesIO()
                combined.export(output, format="mp3", codec="libmp3lame", bitrate="320k")
                return output.getvalue()
                
            else:
                # For monologue format or when no voice2 provided, use single voice
                cleaned_text = re.sub(r'</?(?:Speaker|Person[12])>', '', text)
                synthesis_input = texttospeech_v1beta1.SynthesisInput(text=cleaned_text)
                voice_params = texttospeech_v1beta1.VoiceSelectionParams(
                    language_code="-".join(voice.split("-")[:2]),
                    name=voice,
                )
                audio_config = texttospeech_v1beta1.AudioConfig(
                    audio_encoding=texttospeech_v1beta1.AudioEncoding.MP3
                )
                response = self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice_params,
                    audio_config=audio_config
                )
                return response.audio_content
            
        except Exception as e:
            logger.error(f"Failed to generate audio: {str(e)}")
            raise RuntimeError(f"Failed to generate audio: {str(e)}") from e
    
    def get_supported_tags(self) -> List[str]:
        """Get supported SSML tags."""
        tags = self.COMMON_SSML_TAGS.copy()
        tags.extend(['Speaker', 'Person1', 'Person2'])  # Add all supported tags
        return tags
        
    def validate_parameters(self, text: str, voice: str, model: str) -> None:
        """
        Validate input parameters before generating audio.
        
        Args:
            text (str): Input text
            voice (str): Voice ID/name
            model (str): Model name
            
        Raises:
            ValueError: If parameters are invalid
        """
        super().validate_parameters(text, voice, model)
        
        if not text:
            raise ValueError("Text cannot be empty")
        
        if not voice:
            raise ValueError("Voice must be specified")
            
    def split_qa(self, input_text: str, ending_message: str, supported_tags: List[str] = None) -> List[Tuple[str, str]]:
        """
        Split the input text into pairs for TTS processing.
        Handles both conversation (Person1/Person2) and monologue (Speaker) formats.

        Args:
            input_text (str): The input text containing either Person1/Person2 or Speaker tags
            ending_message (str): The ending message to add to the end of the input text
            supported_tags (List[str]): Optional list of supported tags

        Returns:
            List[Tuple[str, str]]: A list of tuples containing (first_part, second_part) where:
                - For conversation format: (Person1 text, Person2 text)
                - For monologue format: (Speaker text, empty string)
        """
        input_text = self.clean_tss_markup(input_text, supported_tags=supported_tags)
        
        # Check if this is monologue format (Speaker tags)
        if "<Speaker>" in input_text:
            # Split into Speaker sections
            pattern = r"<Speaker>(.*?)</Speaker>"
            matches = re.findall(pattern, input_text, re.DOTALL)
            # For monologue, each Speaker section becomes a "question" with empty "answer"
            return [(text.strip(), "") for text in matches]
        else:
            # Conversation format - use base class implementation for Person1/Person2
            return super().split_qa(input_text, ending_message, supported_tags)
