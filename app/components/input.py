"""Input components for the Podcastfy UI."""

import gradio as gr

def create_input_components():
    """Create input components for text, URL, and file input."""
    with gr.Group():
        with gr.Column():
            file_input = gr.File(
                label="File Input",
                file_types=["image", ".pdf", ".txt"],
                file_count="single",
                type="filepath",
                interactive=True
            )
            gr.Markdown("*Drag & drop or click to upload an image, PDF, or text file*")
            
            text_input = gr.Textbox(
                label="Text Input",
                placeholder="Enter text, directory path, or topic to convert to podcast...",
                lines=5,
                info="You can enter raw text, a directory path containing text files, or a topic to generate content about"
            )
            
            url_input = gr.Textbox(
                label="URL Input",
                placeholder="Enter a URL or directory path",
                info="You can enter a URL, YouTube link, PDF path, or directory path containing text files"
            )
    
    return {
        'text_input': text_input,
        'url_input': url_input,
        'file_input': file_input
    }
