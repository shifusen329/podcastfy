"""Event handlers for progress tracking."""

import gradio as gr
from langsmith import traceable

@traceable(run_name="start_progress", tags=["podcastfy", "progress"])
def start_progress():
    """Initialize progress tracking."""
    # Add run metadata
    run_metadata = {
        "stage": "start",
        "progress": 0
    }
    
    try:
        return [
            gr.Slider(value=0),
            gr.Label(value="Starting...")
        ]
    except Exception as e:
        # Add error metadata
        run_metadata["error"] = str(e)
        run_metadata["error_type"] = type(e).__name__
        print(f"Error starting progress: {str(e)}")
        return [
            gr.Slider(value=0),
            gr.Label(value="Error initializing progress")
        ]

@traceable(run_name="update_progress", tags=["podcastfy", "progress"])
def update_generation_progress(progress, status):
    """Update progress bar and status message."""
    # Add run metadata
    run_metadata = {
        "stage": "update",
        "progress": progress,
        "status": status
    }
    
    try:
        return [
            gr.Slider(value=progress),
            gr.Label(value=status)
        ]
    except Exception as e:
        # Add error metadata
        run_metadata["error"] = str(e)
        run_metadata["error_type"] = type(e).__name__
        print(f"Error updating progress: {str(e)}")
        return [
            gr.Slider(value=progress),
            gr.Label(value=f"Error updating progress: {str(e)}")
        ]

@traceable(run_name="end_progress", tags=["podcastfy", "progress"])
def end_progress(success=True):
    """Complete progress tracking."""
    # Add run metadata
    run_metadata = {
        "stage": "end",
        "success": success
    }
    
    try:
        if success:
            return [
                gr.Slider(value=100),
                gr.Label(value="Complete!")
            ]
        else:
            return [
                gr.Slider(value=0),
                gr.Label(value="Failed")
            ]
    except Exception as e:
        # Add error metadata
        run_metadata["error"] = str(e)
        run_metadata["error_type"] = type(e).__name__
        print(f"Error ending progress: {str(e)}")
        return [
            gr.Slider(value=0),
            gr.Label(value=f"Error completing progress: {str(e)}")
        ]
