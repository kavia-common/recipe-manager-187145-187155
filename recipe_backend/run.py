import os
from app import app

if __name__ == "__main__":
    # Keep bound to existing preview port (default 3001)
    port = int(os.getenv("PORT", "3001"))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host=host, port=port, debug=debug)
