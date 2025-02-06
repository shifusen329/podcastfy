"""Event handlers for progress tracking."""

import gradio as gr
from ..components.progress import STAGES

def start_progress():
    """Initialize progress tracking."""
    # Add run metadata
    run_metadata = {
        "stage": "start",
        "progress": 0
    }
    
    try:
        html = f'''
        <div style="font-size: 0.9em; min-width: 300px;">
            <div>{STAGES[0]} (0%)</div>
        </div>
        '''
        return [gr.HTML(value=html)]
    except Exception as e:
        # Add error metadata
        run_metadata["error"] = str(e)
        run_metadata["error_type"] = type(e).__name__
        print(f"Error starting progress: {str(e)}")
        html = '''
        <div style="font-size: 0.9em; min-width: 300px;">
            <div>Error (0%)</div>
            <div style="color: #666;">Error initializing progress</div>
        </div>
        '''
        return [gr.HTML(value=html)]

def update_generation_progress(stage: int, status: str, progress: float):
    """Update progress tracking components."""
    # Add run metadata
    run_metadata = {
        "stage": stage,
        "status": status,
        "progress": progress
    }
    
    try:
        stage_text = STAGES[stage] if 0 <= stage < len(STAGES) else "Error"
        
        # Only show status if it provides additional information
        status_html = ""
        if status and not status.lower().startswith(stage_text.lower()):
            status_html = f'<div style="color: #666;">{status}</div>'
        
        html = f'''
        <div style="font-size: 0.9em; min-width: 300px;">
            <div>{stage_text} ({progress}%)</div>
            {status_html}
        </div>
        '''
        return [gr.HTML(value=html)]
    except Exception as e:
        # Add error metadata
        run_metadata["error"] = str(e)
        run_metadata["error_type"] = type(e).__name__
        print(f"Error updating progress: {str(e)}")
        html = f'''
        <div style="font-size: 0.9em; min-width: 300px;">
            <div>Error (0%)</div>
            <div style="color: #666;">Error updating progress: {str(e)}</div>
        </div>
        '''
        return [gr.HTML(value=html)]

def end_progress(success=True):
    """Complete progress tracking."""
    # Add run metadata
    run_metadata = {
        "stage": "end",
        "success": success
    }
    
    try:
        if success:
            html = f'''
            <div style="font-size: 0.9em; min-width: 300px;">
                <div>{STAGES[-1]} (100%)</div>
            </div>
            '''
            return [gr.HTML(value=html)]
        else:
            html = '''
            <div style="font-size: 0.9em; min-width: 300px;">
                <div>Error (0%)</div>
                <div style="color: #666;">Failed</div>
            </div>
            '''
            return [gr.HTML(value=html)]
    except Exception as e:
        # Add error metadata
        run_metadata["error"] = str(e)
        run_metadata["error_type"] = type(e).__name__
        print(f"Error ending progress: {str(e)}")
        html = f'''
        <div style="font-size: 0.9em; min-width: 300px;">
            <div>Error (0%)</div>
            <div style="color: #666;">Error completing progress: {str(e)}</div>
        </div>
        '''
        return [gr.HTML(value=html)]
