# app/core/config.py
# Loads environment variables from .env using python-dotenv
# and exposes them as simple settings for the rest of the app.

import os
from dotenv import load_dotenv

# Load variables from .env into the process environment
load_dotenv()

# Application settings read from environment, with sensible defaults
PORT: int = int(os.getenv("PORT", "8000"))
APP_ENV: str = os.getenv("APP_ENV", "development")