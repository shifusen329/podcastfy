"""Style components for the Podcastfy interface."""

import gradio as gr
from ..config.styles import STYLES, ENGAGEMENT_TECHNIQUES, FORMATS
from ..handlers.style import update_style_fields

def get_style_presets(format_type="conversation"):
    """Get predefined style presets for the specified format.
    
    Args:
        format_type: The format type to get presets for (conversation or monologue)
        
    Returns:
        Dictionary of style presets with descriptions
    """
    format_styles = STYLES.get(format_type, {})
    return {name: {"description": ", ".join(style['conversation_style'])} 
            for name, style in format_styles.items()}

def get_dialogue_structures():
    """Get available dialogue structures."""
    from ..config.styles import DIALOGUE_STRUCTURES
    return DIALOGUE_STRUCTURES

def get_engagement_techniques():
    """Get available engagement techniques."""
    return ENGAGEMENT_TECHNIQUES

def get_formats():
    """Get available podcast formats."""
    return {
        format_id: format_info["name"]
        for format_id, format_info in FORMATS.items()
    }

def create_style_components():
    """Create style customization components."""
    with gr.Group():
        # Format Selection
        format_type = gr.Radio(
            choices=list(get_formats().keys()),
            label="Format Type",
            info="Choose the podcast format",
            value="conversation"
        )
        
        # Basic Style
        style = gr.Dropdown(
            choices=list(get_style_presets("conversation").keys()),
            label="Style",
            info="Select a style preset",
            value="engaging"  # Default to engaging style
        )
        
        creativity = gr.Slider(
            minimum=0.0,
            maximum=1.0,
            value=0.7,
            step=0.1,
            label="Creativity",
            info="Adjust the creativity level of the conversation"
        )
        
        # Podcast Details
        podcast_name = gr.Textbox(
            label="Podcast Name",
            info="Optional: Give your podcast a name",
            placeholder="e.g., Tech Insights Daily"
        )
        
        podcast_tagline = gr.Textbox(
            label="Podcast Tagline",
            info="Optional: Add a tagline for your podcast",
            placeholder="e.g., Exploring tomorrow's technology today"
        )
        
        # Structure and Roles
        dialogue_structure = gr.Dropdown(
            choices=get_dialogue_structures(),
            label="Dialogue Structure",
            info="Optional: Choose the conversation format",
            value="Discussions"  # Default to Discussions for conversation format
        )
        
        # Role fields in a group for conditional visibility
        with gr.Group() as roles_group:
            with gr.Row():
                # Get default roles from engaging style
                default_roles = STYLES['conversation']['engaging']
                role1 = gr.Textbox(
                    label="Role 1",
                    info="Optional: Define the first speaker's role",
                    placeholder="e.g., Host or Narrator",
                    value=default_roles['roles_person1']
                )
                
                role2 = gr.Textbox(
                    label="Role 2",
                    info="Optional: Define the second speaker's role",
                    placeholder="e.g., Guest",
                    visible=True,  # Initially visible since conversation is default
                    value=default_roles['roles_person2']
                )
        
        # Engagement and Instructions
        # Get default engagement techniques from engaging style
        default_engagement = STYLES['conversation']['engaging']['engagement_techniques']
        engagement = gr.Dropdown(
            choices=get_engagement_techniques(),
            label="Engagement Techniques",
            info="Optional: Select techniques to make the content engaging",
            multiselect=True,
            value=default_engagement
        )
        
        user_instructions = gr.Textbox(
            label="Custom Instructions",
            info="Optional: Add specific instructions",
            placeholder="e.g., Focus on practical examples and real-world applications",
            lines=3
        )
    
    # Update components based on format change
    def update_format_components(format_type):
        format_info = FORMATS[format_type]
        role1_label = format_info["roles"][0]
        
        # Get style choices for the selected format
        style_choices = list(get_style_presets(format_type).keys())
        
        # Set default style and dialogue structure based on format
        default_style = "engaging" if format_type == "conversation" else "narrative"
        default_structure = "Discussions" if format_type == "conversation" else "Topic Introduction"
        
        return {
            role1: gr.update(label=f"Role ({role1_label})"),
            role2: gr.update(
                visible=format_info["supports_roles"],
                label="Role (Guest)" if format_info["supports_roles"] else ""
            ),
            style: gr.update(choices=style_choices, value=default_style),
            dialogue_structure: gr.update(value=default_structure)
        }
    
    # Update components based on style change
    def update_style_components(style, format_type, current_engagement):
        # Get style updates
        style_updates = update_style_fields(style, format_type, current_engagement)
        
        return {
            role1: gr.update(value=style_updates[0]),
            role2: gr.update(value=style_updates[1]),
            engagement: gr.update(value=style_updates[2])
        }

    # Register event handlers
    format_type.change(
        fn=update_format_components,
        inputs=[format_type],
        outputs=[role1, role2, style, dialogue_structure]
    )

    style.change(
        fn=update_style_components,
        inputs=[style, format_type, engagement],
        outputs=[role1, role2, engagement]
    )
    
    return {
        'format_type': format_type,
        'style': style,
        'creativity': creativity,
        'podcast_name': podcast_name,
        'podcast_tagline': podcast_tagline,
        'dialogue_structure': dialogue_structure,
        'role1': role1,
        'role2': role2,
        'engagement': engagement,
        'user_instructions': user_instructions
    }
