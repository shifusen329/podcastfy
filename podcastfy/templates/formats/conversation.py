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
1. Tag Usage:
   - Use <Person1> and <Person2> tags for all dialogue
   - Each speaker's line must be in their own tags
   - Tags must be adjacent (e.g., </Person1><Person2>)
   - No nested or repeated tags (e.g., avoid </Person1><Person1>)

2. Speaker Roles:
   - Person1 and Person2 maintain distinct roles
   - Keep roles consistent throughout
   - No switching roles between speakers

3. Dialogue Structure:
   - Alternate between speakers
   - Each line must be a complete thought
   - No run-on dialogue
   - No untagged speech

Example format:
<Person1>Welcome to the show.</Person1>
<Person2>Thank you for having me.</Person2>
<Person1>Let's begin with our first topic.</Person1>
<Person2>I'd be happy to discuss that.</Person2>"""

    def get_longform_instructions(self) -> str:
        """Get format-specific instructions for longform content."""
        print(f"\n=== Getting Conversation Longform Instructions ===")
        instructions = """
Format Rules for Long-form Conversation:
1. Tag Usage:
   - Use <Person1> and <Person2> tags for all dialogue
   - Each speaker's line must be in their respective tags
   - Tags must be properly closed
   - No untagged speech

2. Speaker Alternation:
   - Look at the last speaker in CONTEXT
   - If Person1 spoke last, start with Person2
   - If Person2 spoke last, start with Person1
   - Maintain strict alternation between speakers
   - No consecutive same-speaker lines

3. Speaker Roles:
   - Person1 guides discussion and asks questions
   - Person2 provides insights and detailed responses
   - Keep roles consistent throughout
   - No switching roles between speakers

4. Flow Rules:
   - Continue directly from previous context
   - No meta-commentary about parts or breaks
   - No greetings or farewells except when instructed
   - Keep conversation flowing naturally
   - Each line must build on previous context"""
        print(f"Instructions:\n{instructions}")
        return instructions
