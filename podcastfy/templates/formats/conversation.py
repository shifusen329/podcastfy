"""Conversation format template for podcast generation."""

from ..base import PodcastTemplate

class ConversationTemplate(PodcastTemplate):
    """Template for generating conversation-style podcasts."""
    
    def __init__(self):
        """Initialize conversation template."""
        super().__init__("conversation")
        self.supported_tags = ["Person1", "Person2"]
    
    def get_template(self) -> str:
        """Get the conversation template string."""
        return """Format Requirements:
1. Use <Person1> and <Person2> tags to mark speaker turns
2. Each speaker's dialogue must be enclosed in their respective tags
3. Maintain clear roles for each speaker
4. Ensure speakers take turns in a natural back-and-forth flow
5. Do not nest or repeat tags (e.g., avoid </Person1><Person1>)
6. Each speaker's line should be a complete thought

Example format:
<Person1>Hello and welcome to the show!</Person1>
<Person2>Thanks for having me. Let's dive into today's topic.</Person2>
<Person1>Our first point is...</Person1>"""
