"""Input components for the Podcastfy UI."""

import gradio as gr

def create_input_components():
    """Create reorganized input components."""
    with gr.Group():
        gr.Markdown("### Input Settings")
        
        # File Input (at top)
        with gr.Row():
            file_input = gr.File(
                label="File Input (images, PDFs, text files)",
                file_types=["image", ".pdf", ".txt"],
                file_count="multiple",
                type="filepath",
                interactive=True
            )
        
        # Text Input (merged with topic)
        with gr.Row():
            text_input = gr.Textbox(
                label="Text or Topic Input",
                info="Enter text directly or a topic to generate content about",
                lines=5
            )
        
        # URL Input (multiple URLs)
        with gr.Row():
            url_input = gr.Textbox(
                label="URLs",
                info="Enter one or more URLs (one per line)",
                lines=3
            )
        
        # Directory Group
        with gr.Group():
            with gr.Row():
                directory_input = gr.Textbox(
                    label="Directory Path",
                    info="Enter path to directory containing files to process",
                    placeholder="/path/to/directory"
                )
            with gr.Row():
                with gr.Column(scale=1):
                    recursive = gr.Checkbox(
                        label="Process Subdirectories",
                        value=False,
                        info="Include files in subdirectories"
                    )
                with gr.Column(scale=1):
                    file_types = gr.Dropdown(
                        label="File Types",
                        choices=["All Files", "pdf", "txt", "jpg", "png"],
                        multiselect=True,
                        value="All Files",
                        info="Select file types to process"
                    )
    
    return {
        'text_input': text_input,
        'url_input': url_input,
        'file_input': file_input,
        'directory_input': directory_input,
        'recursive': recursive,
        'file_types': file_types
    }
