import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def create_openai_client():
    """Erstellt den zentralen OpenAI-Client."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY wurde nicht gefunden. "
            "Prüfe deine .env-Datei."
        )

    return OpenAI(
        api_key=api_key
    )


client = create_openai_client()
