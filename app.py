"""Entry point for the Podcastfy UI application."""

from app import create_app

if __name__ == "__main__":
    demo = create_app()
    demo.launch(server_name="0.0.0.0")
