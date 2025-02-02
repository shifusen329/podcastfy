"""Progress tracking components for the Podcastfy UI."""

import gradio as gr

STAGES = [
    "Initializing",
    "Processing Input",
    "Generating Transcript",
    "Starting TTS",
    "Processing TTS Chunks",
    "Combining Audio",
    "Complete"
]

def create_progress_components():
    """Create progress tracking components with compact layout."""
    with gr.Group():
        # Combined progress and status indicator
        progress_status = gr.HTML(
            value='<div style="font-size: 0.9em; min-width: 300px;">Ready to generate podcast</div>',
            label="Progress"
        )
    
    return {
        'stages': progress_status,  # Keep the same key for compatibility
        'bar': progress_status,     # Both point to the same component
        'status': progress_status   # All point to the same component now
    }

def update_progress(stage: int, progress: float = None, status: str = None):
    """Update progress components."""
    stage_text = STAGES[stage] if 0 <= stage < len(STAGES) else "Error"
    progress_text = f" ({progress}%)" if progress is not None else ""
    
    # Only show status if it provides additional information
    status_html = ""
    if status and not status.lower().startswith(stage_text.lower()):
        status_html = f'<div style="color: #666;">{status}</div>'
    
    html = f'''
    <div style="font-size: 0.9em; min-width: 300px;">
        <div>{stage_text}{progress_text}</div>
        {status_html}
    </div>
    '''
    
    return [gr.HTML(value=html)]

def reset_progress():
    """Reset progress tracking to initial state."""
    html = '<div style="font-size: 0.9em; min-width: 300px;">Ready to generate podcast</div>'
    return [gr.HTML(value=html)]
