"""Monologue format template for podcast generation."""

from ..base import PodcastTemplate
import re

class MonologueTemplate(PodcastTemplate):
    """Template for generating monologue-style podcasts."""
    
    def __init__(self):
        """Initialize monologue template."""
        super().__init__("monologue")
        self.supported_tags = ["Speaker"]
        self.conversation_tags = ["Person1", "Person2"]  # Tags to convert
    
    def clean_markup(self, text: str) -> str:
        """Clean markup tags in the text.
        
        Override base method to handle conversation-style tags first.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text with only supported tags
        """
        # First convert any conversation-style tags to monologue format
        text = self._convert_conversation_tags(text)
        
        # Then combine multiple Speaker tags into one continuous speech
        text = self._combine_speaker_tags(text)
        
        # Then apply base cleaning
        return super().clean_markup(text)
    
    def _convert_conversation_tags(self, text: str) -> str:
        """Convert conversation-style tags to monologue format.
        
        Args:
            text: Text to convert
            
        Returns:
            Text with conversation tags converted to monologue format
        """
        # Replace opening tags
        for tag in self.conversation_tags:
            text = re.sub(
                f'<{tag}>', 
                '<Speaker>', 
                text
            )
            text = re.sub(
                f'</{tag}>', 
                '</Speaker>', 
                text
            )
        
        # Clean up any remaining conversation markers
        text = re.sub(r'\[.*?\]', '', text)  # Remove square brackets
        text = re.sub(r'\(.*?\)', '', text)  # Remove parentheses
        
        return text
    
    def _combine_speaker_tags(self, text: str) -> str:
        """Combine multiple Speaker tags into one continuous speech.
        
        Args:
            text: Text to combine
            
        Returns:
            Text with all Speaker sections combined into one
        """
        # Extract all Speaker content
        pattern = r'<Speaker>(.*?)</Speaker>'
        matches = re.findall(pattern, text, re.DOTALL)
        
        if not matches:
            return text
            
        # Combine all content with proper spacing
        combined_content = ' '.join(match.strip() for match in matches)
        
        # Return single Speaker tag with combined content
        return f'<Speaker>{combined_content}</Speaker>'
    
    def get_template(self) -> str:
        """Get the monologue template string."""
        return """Format Requirements:
1. Use <Speaker> tags to mark all speech segments
2. Present as a single narrator throughout
3. Use natural pauses between segments
4. All content will be combined into a single continuous speech"""
