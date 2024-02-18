import os
import sys
from dotenv import load_dotenv


def get_openai_key():
    """Reads the OpenAI API key from the environment or a .env file."""

    # Define the possible locations for the .env file
    dotenv_paths = [
      os.path.join(os.path.dirname(__file__), '..', '.env'),  # Parent directory
      os.path.join(os.path.dirname(__file__), '..', '..', '.env'),  # Grandparent directory
      os.path.join(os.path.expanduser("~"), ".env"),  # Home directory
    ]

    # Try to load the .env file from the possible locations
    for dotenv_path in dotenv_paths:
      if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        break

    # Get the API key from the environment variables
    api_key = os.getenv("OPENAI_API_KEY")

    # Raise an error if the API key is not found
    if api_key is None:
      raise ValueError(
        "OPENAI_API_KEY not found in environment variables or .env file."
      )
    return api_key
