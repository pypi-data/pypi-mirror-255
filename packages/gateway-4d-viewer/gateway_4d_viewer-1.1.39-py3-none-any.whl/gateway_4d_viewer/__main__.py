"""Simple entry point for application."""
import logging

from gateway_4d_viewer import app

if __name__ == "__main__":
    app.run(debug=True)
else:
    # setup logging for when gunicorn is running the app
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
