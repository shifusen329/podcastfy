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
                logger.info(f"\nGenerating Person1 audio segments ({len(person1_matches)} segments):")
                for i, content in enumerate(person1_matches, 1):
                    logger.info(f"\nPerson1 Segment {i}/{len(person1_matches)}:")
                    logger.info(f"Content length: {len(content)} chars")
                    logger.info(f"Content preview: {content[:100]}...")
                    
                    synthesis_input = texttospeech_v1beta1.SynthesisInput(text=content.strip())
                    voice_params = texttospeech_v1beta1.VoiceSelectionParams(
                        language_code="-".join(voice.split("-")[:2]),
                        name=voice,
                    )
                    audio_config = texttospeech_v1beta1.AudioConfig(
                        audio_encoding=texttospeech_v1beta1.AudioEncoding.MP3
                    )
                    
                    logger.info(f"Sending TTS request for Person1 segment {i}...")
                    response = self.client.synthesize_speech(
                        input=synthesis_input,
                        voice=voice_params,
                        audio_config=audio_config
                    )
                    logger.info(f"Received audio response: {len(response.audio_content)/1024:.1f}KB")
                    person1_audio.append(response.audio_content)
                
                # Generate audio for Person2 content
                person2_audio = []
                logger.info(f"\nGenerating Person2 audio segments ({len(person2_matches)} segments):")
                for i, content in enumerate(person2_matches, 1):
                    logger.info(f"\nPerson2 Segment {i}/{len(person2_matches)}:")
                    logger.info(f"Content length: {len(content)} chars")
                    logger.info(f"Content preview: {content[:100]}...")
                    
                    synthesis_input = texttospeech_v1beta1.SynthesisInput(text=content.strip())
                    voice_params = texttospeech_v1beta1.VoiceSelectionParams(
                        language_code="-".join(voice2.split("-")[:2]),
                        name=voice2,
                    )
                    audio_config = texttospeech_v1beta1.AudioConfig(
                        audio_encoding=texttospeech_v1beta1.AudioEncoding.MP3
                    )
                    
                    logger.info(f"Sending TTS request for Person2 segment {i}...")
                    response = self.client.synthesize_speech(
                        input=synthesis_input,
                        voice=voice_params,
                        audio_config=audio_config
                    )
                    logger.info(f"Received audio response: {len(response.audio_content)/1024:.1f}KB")
                    person2_audio.append(response.audio_content)
                
                # Merge audio segments alternating between Person1 and Person2
                from pydub import AudioSegment
                import io
                
                logger.info("\nMerging audio segments:")
                combined = AudioSegment.empty()
                total_duration = 0
                
                for i, (p1, p2) in enumerate(zip(person1_audio, person2_audio), 1):
                    logger.info(f"\nProcessing pair {i}/{min(len(person1_audio), len(person2_audio))}:")
                    
                    # Add Person1 audio
                    segment = AudioSegment.from_file(io.BytesIO(p1))
                    duration = len(segment)/1000
                    total_duration += duration
                    logger.info(f"Person1 duration: {duration:.1f}s")
                    combined += segment
                    
                    # Add Person2 audio
                    segment = AudioSegment.from_file(io.BytesIO(p2))
                    duration = len(segment)/1000
                    total_duration += duration
                    logger.info(f"Person2 duration: {duration:.1f}s")
                    combined += segment
                
                # Handle any remaining Person1 audio
                if len(person1_audio) > len(person2_audio):
                    logger.info("\nProcessing final Person1 segment:")
                    segment = AudioSegment.from_file(io.BytesIO(person1_audio[-1]))
                    duration = len(segment)/1000
                    total_duration += duration
                    logger.info(f"Duration: {duration:.1f}s")
                    combined += segment
                
                logger.info(f"\nTotal duration: {total_duration:.1f}s")
                
                # Export combined audio
                logger.info("\nExporting combined audio...")
                output = io.BytesIO()
                combined.export(output, format="mp3", codec="libmp3lame", bitrate="320k")
                final_audio = output.getvalue()
                logger.info(f"Final audio size: {len(final_audio)/1024:.1f}KB")
                return final_audio
                
            else:
                # For monologue format or when no voice2 provided, use single voice
                logger.info("\nProcessing monologue format:")
                
                # Extract Speaker content
                speaker_pattern = r'<Speaker>(.*?)</Speaker>'
                speaker_matches = re.findall(speaker_pattern, text, re.DOTALL)
                
                # Generate audio for Speaker content
                speaker_audio = []
                logger.info(f"\nGenerating Speaker audio segments ({len(speaker_matches)} segments):")
                for i, content in enumerate(speaker_matches, 1):
                    logger.info(f"\nSpeaker Segment {i}/{len(speaker_matches)}:")
                    logger.info(f"Content length: {len(content)} chars")
                    logger.info(f"Content preview: {content[:100]}...")
                    
                    synthesis_input = texttospeech_v1beta1.SynthesisInput(text=content.strip())
                    voice_params = texttospeech_v1beta1.VoiceSelectionParams(
                        language_code="-".join(voice.split("-")[:2]),
                        name=voice,
                    )
                    audio_config = texttospeech_v1beta1.AudioConfig(
                        audio_encoding=texttospeech_v1beta1.AudioEncoding.MP3
                    )
                    
                    logger.info(f"Sending TTS request for Speaker segment {i}...")
                    response = self.client.synthesize_speech(
                        input=synthesis_input,
                        voice=voice_params,
                        audio_config=audio_config
                    )
                    logger.info(f"Received audio response: {len(response.audio_content)/1024:.1f}KB")
                    speaker_audio.append(response.audio_content)
                
                # Merge audio segments
                from pydub import AudioSegment
                import io
                
                logger.info("\nMerging audio segments:")
                combined = AudioSegment.empty()
                total_duration = 0
                
                for i, p1 in enumerate(speaker_audio, 1):
                    logger.info(f"\nProcessing segment {i}/{len(speaker_audio)}:")
                    
                    # Add Speaker audio
                    segment = AudioSegment.from_file(io.BytesIO(p1))
                    duration = len(segment)/1000
                    total_duration += duration
                    logger.info(f"Duration: {duration:.1f}s")
                    combined += segment
                
                logger.info(f"\nTotal duration: {total_duration:.1f}s")
                
                # Export combined audio
                logger.info("\nExporting combined audio...")
                output = io.BytesIO()
                combined.export(output, format="mp3", codec="libmp3lame", bitrate="320k")
                final_audio = output.getvalue()
                logger.info(f"Final audio size: {len(final_audio)/1024:.1f}KB")
                return final_audio
            
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
