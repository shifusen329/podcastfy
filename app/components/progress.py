"""Progress tracking components for the Podcastfy UI."""

import gradio as gr

def create_progress_components():
    """Create progress tracking components."""
    with gr.Group():
        with gr.Row():
            progress_bar = gr.Slider(
                minimum=0,
                maximum=100,
                value=0,
                label="Generation Progress",
                interactive=False
            )
        with gr.Row():
            status_label = gr.Label(
                label="Status",
                value="Ready to generate podcast"
            )
    
    return {
        'bar': progress_bar,
        'status': status_label
    }

def update_progress(progress, status=None):
    """Update progress bar and status label."""
    updates = [gr.Slider(value=progress)]
    if status:
        updates.append(gr.Label(value=status))
    return updates

def reset_progress():
    """Reset progress tracking to initial state."""
    return [
        gr.Slider(value=0),
        gr.Label(value="Ready to generate podcast")
    ]
