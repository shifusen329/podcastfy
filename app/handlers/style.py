"""Style-related event handlers for the Podcastfy interface."""

import gradio as gr
from ..config.styles import STYLES, FORMATS

def update_style_fields(style, format_type="conversation", current_engagement=None):
    """Update fields based on selected style and format.
    
    Args:
        style: Selected style preset
        format_type: Selected format type (conversation or monologue)
        current_engagement: Currently selected engagement techniques
        
    Returns:
        List containing updated values for role1, role2, and engagement fields
    """
    # Initialize with empty engagement if not provided
    if current_engagement is None:
        current_engagement = []

    # Get format-specific styles
    format_styles = STYLES.get(format_type, {})
    
    if not style or style not in format_styles:
        # Default values based on format
        format_info = FORMATS[format_type]
        if format_type == "monologue":
            return [
                "Narrator",           # role1
                "",                  # role2
                current_engagement   # preserve current engagement
            ]
        else:
            return [
                "Host",              # role1
                "Guest",             # role2
                current_engagement   # preserve current engagement
            ]
    
    # Get style preset for the specific format
    style_preset = format_styles[style]
    
    # Adapt roles based on format
    if format_type == "monologue":
        role1 = "Narrator"
        role2 = ""
    else:
        role1 = style_preset.get('roles_person1', 'Host')
        role2 = style_preset.get('roles_person2', 'Guest')
    
    # Merge current engagement with preset's suggested techniques
    suggested_techniques = style_preset.get('engagement_techniques', [])
    merged_engagement = list(set(current_engagement + suggested_techniques))
    
    return [
        role1,
        role2,
        merged_engagement
    ]

def validate_style_config(format_type, config):
    """Validate style configuration based on format.
    
    Args:
        format_type: Selected format type
        config: Style configuration dictionary
        
    Raises:
        ValueError: If configuration is invalid for the selected format
    """
    format_info = FORMATS[format_type]
    
    if not format_info["supports_roles"] and config.get("roles_person2"):
        raise ValueError(f"{format_info['name']} format does not support multiple roles")
    
    if format_type == "monologue":
        if config.get("roles_person1") and config["roles_person1"] != "Narrator":
            config["roles_person1"] = "Narrator"
