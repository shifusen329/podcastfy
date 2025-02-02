# Podcastfy Development Fork

This is a development fork of [Podcastfy](https://github.com/souzatharsis/podcastfy) with additional features and local customizations.

## Additional Features

- Novel AI TTS integration
- Kokoro TTS integration
- Enhanced voice selection for cloud providers
- Local LLM support (planned)
- Sequential workflow options (planned)

## Development Roadmap

See [TODO.md](TODO.md) for the complete list of planned features and improvements.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/podcastfy-dev.git
cd podcastfy-dev
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:
```
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
# Add other API keys as needed
```

4. Run the application:
```bash
python app.py
```

## Directory Structure

```
podcastfy-dev/
├── app/                    # Gradio UI application
├── podcastfy/             # Core package
├── data/                  # Generated content
│   ├── audio/            # Generated audio files
│   └── transcripts/      # Generated transcripts
├── novel_ai_tts.py       # Novel AI TTS provider
├── kokoro_tts.py         # Kokoro TTS provider
└── app.py                # Application entry point
```

## Contributing

1. Check the [TODO.md](TODO.md) file for planned features
2. Create a new branch for your feature
3. Submit a pull request with your changes

## License

This software is licensed under [Apache 2.0](LICENSE).
