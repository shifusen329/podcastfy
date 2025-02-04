"""Novel AI TTS provider implementation."""

import requests
import re
from typing import Optional
from ..base import TTSProvider

class NovelAITTS(TTSProvider):
    """Novel AI Text-to-Speech provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "novel-ai-tts-1"):
        """
        Initialize Novel AI TTS provider.
        
        Args:
            api_key: Not used, kept for compatibility
            model: Model name to use. Defaults to "novel-ai-tts-1"
        """
        self.base_url = "http://localhost:8001/v1"
        self.model = model
            
    def generate_audio(self, text: str, voice: str, model: str, voice2: str = None) -> bytes:
        """Generate audio using Novel AI API with support for two voices."""
        self.validate_parameters(text, voice, model)
        
        try:
            # Split text into Person1 and Person2 parts using regex
            parts = []
            
            # Extract text between Person tags using regex
            pattern = r'<Person1>(.*?)</Person1>|<Person2>(.*?)</Person2>'
            matches = re.finditer(pattern, text, re.DOTALL)
            
            for match in matches:
                if match.group(1) is not None:  # Person1
                    text_part = match.group(1).strip()
                    if text_part:
                        parts.append((text_part, voice))
                elif match.group(2) is not None:  # Person2
                    text_part = match.group(2).strip()
                    if text_part:
                        parts.append((text_part, voice2 or "Aini"))
            
            # Generate audio for each part
            audio_parts = []
            for text_part, voice_part in parts:
                response = requests.post(
                    f"{self.base_url}/audio/speech",
                    json={
                        "model": model,
                        "input": text_part,
                        "voice": voice_part
                    }
                )
                if response.status_code == 200:
                    audio_parts.append(response.content)
                else:
                    raise RuntimeError(f"API error: {response.text}")
                    
            # Combine all audio parts
            if not audio_parts:
                raise RuntimeError("No audio parts generated")
                
            return b''.join(audio_parts)
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate audio: {str(e)}") from e
