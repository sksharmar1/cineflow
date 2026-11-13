import os
import sys

# Make the `app` package importable inside Vercel's serverless runtime.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402,F401  (Vercel serves this ASGI `app`)
