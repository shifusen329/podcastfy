"""Templates package for podcast generation."""

from .base import PodcastTemplate
from .formats.conversation import ConversationTemplate
from .formats.monologue import MonologueTemplate

__all__ = [
    "PodcastTemplate",
    "ConversationTemplate",
    "MonologueTemplate"
]
