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
1. Tag Usage:
   - Use <Speaker> tags for all content
   - Each paragraph must be in its own tag
   - Tags must be properly closed
   - No nested or repeated tags

2. Paragraph Structure:
   - One complete thought per paragraph
   - Each paragraph in its own <Speaker> tag
   - No run-on paragraphs
   - No untagged text

3. Voice Format:
   - Single speaker throughout
   - First-person perspective
   - No dialogue or multiple voices

Example format:
<Speaker>Welcome to this discussion.</Speaker>
<Speaker>Let me share my thoughts on this topic.</Speaker>
<Speaker>Here's what I've discovered in my research.</Speaker>"""

    def get_longform_instructions(self) -> str:
        """Get format-specific instructions for longform content."""
        print(f"\n=== Getting Monologue Longform Instructions ===")
        instructions = """
Format Rules for Long-form Monologue:
1. Tag Usage:
   - Use <Speaker> tags for each paragraph
   - Each paragraph must be in its own tag
   - Tags must be properly closed
   - No untagged text

2. Paragraph Structure:
   - Each new thought in a separate <Speaker> tag
   - Keep paragraphs focused and complete
   - Use clear topic transitions
   - No run-on paragraphs
   - Each paragraph must build on previous context

3. Voice Format:
   - Maintain same narrative voice throughout
   - Keep consistent first-person perspective
   - Use single speaker throughout
   - No dialogue or multiple voices
   - Keep tone and style consistent

4. Flow Rules:
   - Continue directly from previous context
   - No meta-commentary about parts or breaks
   - No greetings or farewells except when instructed
   - Keep narrative flowing naturally
   - Each paragraph must connect to the next"""
        print(f"Instructions:\n{instructions}")
        return instructions
