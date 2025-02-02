"""Input components for the Podcastfy UI."""

import gradio as gr

def create_input_components():
    """Create input components for text and URL input."""
    with gr.Group():
        text_input = gr.Textbox(
            label="Text Input",
            placeholder="Enter text, directory path, or topic to convert to podcast...",
            lines=5,
            info="You can enter raw text, a directory path containing text files, or a topic to generate content about"
        )
        url_input = gr.Textbox(
            label="URL Input",
            placeholder="Or enter a URL or directory path to generate podcast from...",
            info="You can enter a URL, YouTube link, PDF path, or directory path containing text files"
        )
    
    return {
        'text_input': text_input,
        'url_input': url_input
    }
