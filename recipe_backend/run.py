import os

# Load environment variables from .env if present, but do not require it
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()  # safe: no error if .env not present
except Exception:
    # If python-dotenv isn't installed or any issue occurs, proceed without it
    pass

# Import app factory and construct app instance for running
from app import create_app  # noqa: E402

app = create_app()

# PUBLIC_INTERFACE
if __name__ == "__main__":
    """
    Flask application entrypoint.

    Environment:
        - PORT: Server port (default 3001)
        - HOST: Bind host (default 0.0.0.0)
        - FLASK_ENV: 'development' enables debug

    Starts the server listening on HOST:PORT.
    """
    port = int(os.getenv("PORT", "3001"))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host=host, port=port, debug=debug)
