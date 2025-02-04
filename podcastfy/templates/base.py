"""Base template class for podcast generation."""

from typing import List, Dict, Any
import re

class PodcastTemplate:
    """Base class for podcast templates.
    
    This class defines the interface and common functionality for all podcast templates.
    Each format (conversation, monologue, etc.) should subclass this and implement
    its specific behavior.
    """
    
    def __init__(self, format_type: str):
        """Initialize template.
        
        Args:
            format_type: Type of podcast format (e.g., "conversation", "monologue")
        """
        self.format_type = format_type
        self.supported_tags: List[str] = []
        self.required_params: List[str] = [
            "conversation_style",
            "dialogue_structure",
            "engagement_techniques",
            "podcast_name",
            "podcast_tagline"
        ]
    
    def validate_params(self, params: Dict[str, Any]) -> None:
        """Validate that all required parameters are present.
        
        Args:
            params: Dictionary of template parameters
            
        Raises:
            ValueError: If any required parameter is missing
        """
        missing = [p for p in self.required_params if p not in params]
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")
    
    def clean_markup(self, text: str) -> str:
        """Clean markup tags in the text.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text with only supported tags
        """
        # First clean any scratchpad or plaintext blocks
        text = self._clean_scratchpad(text)
        
        # Then clean markup tags
        text = self._clean_markup_tags(text)
        
        # Finally fix any malformed tags
        text = self._fix_malformed_tags(text)
        
        return text
    
    def _clean_scratchpad(self, text: str) -> str:
        """Remove scratchpad blocks and other unwanted markup.
        
        Args:
            text: Text to clean
            
        Returns:
            Text with scratchpad blocks and unwanted markup removed
        """
        try:
            # Remove scratchpad blocks, plaintext blocks, standalone backticks
            pattern = r'```scratchpad\n.*?```\n?|```plaintext\n.*?```\n?|```\n?|\[.*?\]'
            cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
            
            # Remove "xml" if followed by a closing tag
            tag_pattern = "|".join(self.supported_tags)
            cleaned_text = re.sub(
                f"xml(?=\s*</(?:{tag_pattern})>)",
                "",
                cleaned_text
            )
            
            # Remove underscores around words
            cleaned_text = re.sub(r'_(.*?)_', r'\1', cleaned_text)
            
            return cleaned_text.strip()
            
        except Exception as e:
            # Log error but return original text
            print(f"Error cleaning scratchpad content: {str(e)}")
            return text
    
    def _clean_markup_tags(self, text: str) -> str:
        """Remove unsupported markup tags while preserving supported ones.
        
        Args:
            text: Text to clean
            
        Returns:
            Text with only supported tags remaining
        """
        try:
            # Define supported tags (format-specific tags + common ones)
            supported = ["speak", "lang", "p", "phoneme", "s", "sub"]
            supported.extend(self.supported_tags)
            
            # Remove any tags that aren't in supported list
            pattern = r"</?(?!(?:" + "|".join(supported) + r")\b)[^>]+>"
            cleaned_text = re.sub(pattern, "", text)
            
            # Clean up extra newlines
            cleaned_text = re.sub(r"\n\s*\n", "\n", cleaned_text)
            
            # Remove asterisks
            cleaned_text = re.sub(r"\*", "", cleaned_text)
            
            # Ensure all supported tags are properly closed
            for tag in self.supported_tags:
                cleaned_text = re.sub(
                    f'<{tag}>(.*?)(?=<(?:{"|".join(self.supported_tags)})>|$)',
                    f"<{tag}>\\1</{tag}>",
                    cleaned_text,
                    flags=re.DOTALL
                )
            
            return cleaned_text.strip()
            
        except Exception as e:
            # Log error but return original text
            print(f"Error cleaning markup tags: {str(e)}")
            return text
            
    def _fix_malformed_tags(self, text: str) -> str:
        """Fix malformed tags like consecutive closing/opening tags.
        
        Args:
            text: Text to fix
            
        Returns:
            Text with fixed tags
        """
        try:
            # Fix consecutive closing/opening tags of the same type
            for tag in self.supported_tags:
                # Replace </tag><tag> with a space
                pattern = f'</{tag}>\s*<{tag}>'
                text = re.sub(pattern, ' ', text)
            
            # Clean up any extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            # Ensure proper spacing around tags
            for tag in self.supported_tags:
                # Add space after closing tag if followed by another tag
                text = re.sub(f'</{tag}>(<[^>]+>)', f'</{tag}> \\1', text)
                # Add space before opening tag if preceded by text
                text = re.sub(f'([^>\s])(<{tag}>)', '\\1 \\2', text)
            
            return text.strip()
            
        except Exception as e:
            # Log error but return original text
            print(f"Error fixing malformed tags: {str(e)}")
            return text
    
    def get_template(self) -> str:
        """Get the template string.
        
        This method should be overridden by subclasses to provide their specific template.
        
        Returns:
            Template string for this format
            
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement get_template()")

    def get_longform_instructions(self) -> str:
        """Get format-specific instructions for longform content.
        
        This method should be overridden by subclasses to provide their specific
        longform generation instructions.
        
        Returns:
            Format-specific instructions for longform content
            
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement get_longform_instructions()")
