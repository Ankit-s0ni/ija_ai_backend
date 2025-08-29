# Vercel Python Function entrypoint for FastAPI
# Exposes the FastAPI ASGI app defined in app.main

from app.main import app  # Vercel Python runtime detects ASGI via `app`
