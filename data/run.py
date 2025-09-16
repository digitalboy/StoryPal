# run.py
from app import create_app
from app.config import Config
import logging

# This check is important to ensure that the app is created
# only when the script is executed directly.
if __name__ == "__main__":
    # The app factory pattern is used here.
    app = create_app()

    # This is for development only. For production, use a WSGI server.
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
