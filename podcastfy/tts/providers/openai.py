"""OpenAI TTS provider implementation."""

import openai
from typing import List, Optional, Tuple
from ..base import TTSProvider
import re
import io
from pydub import AudioSegment

class OpenAITTS(TTSProvider):
    """OpenAI Text-to-Speech provider."""
    
    # Provider-specific SSML tags
    PROVIDER_SSML_TAGS: List[str] = ['break', 'emphasis', 'Speaker', 'Person1', 'Person2']
    
    def __init__(self, api_key: Optional[str] = None, model: str = "tts-1-hd"):
        """
        Initialize OpenAI TTS provider.
        
        Args:
            api_key: OpenAI API key. If None, expects OPENAI_API_KEY env variable
            model: Model name to use. Defaults to "tts-1-hd"
        """
        if api_key:
            openai.api_key = api_key
        elif not openai.api_key:
            raise ValueError("OpenAI API key must be provided or set in environment")
        self.model = model
            
    def get_supported_tags(self) -> List[str]:
        """Get all supported SSML tags including provider-specific ones."""
        return self.PROVIDER_SSML_TAGS
        
    def generate_audio(self, text: str, voice: str = "echo", model: str = None, voice2: str = None) -> bytes:
        """Generate audio using OpenAI API."""
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
                    response = openai.audio.speech.create(
                        model=model or self.model,
                        voice=voice,
                        input=content.strip()
                    )
                    person1_audio.append(response.content)
                
                # Generate audio for Person2 content
                person2_audio = []
                for content in person2_matches:
                    response = openai.audio.speech.create(
                        model=model or self.model,
                        voice=voice2,
                        input=content.strip()
                    )
                    person2_audio.append(response.content)
                
                # Merge audio segments alternating between Person1 and Person2
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
                response = openai.audio.speech.create(
                    model=model or self.model,
                    voice=voice,
                    input=cleaned_text
                )
                return response.content
                
        except Exception as e:
            raise RuntimeError(f"Failed to generate audio: {str(e)}") from e
