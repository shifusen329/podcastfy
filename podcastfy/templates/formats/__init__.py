"""Format-specific templates for podcast generation."""

from .conversation import ConversationTemplate
from .monologue import MonologueTemplate

__all__ = [
    "ConversationTemplate",
    "MonologueTemplate"
]

# Template registry for easy lookup
TEMPLATES = {
    "conversation": ConversationTemplate,
    "monologue": MonologueTemplate
}

def get_template(format_type: str):
    """Get template class for specified format.
    
    Args:
        format_type: Type of podcast format (e.g., "conversation", "monologue")
        
    Returns:
        Template class for specified format
        
    Raises:
        ValueError: If format type is not supported
    """
    if format_type not in TEMPLATES:
        raise ValueError(
            f"Unsupported format: {format_type}. "
            f"Supported formats: {', '.join(TEMPLATES.keys())}"
        )
    return TEMPLATES[format_type]
