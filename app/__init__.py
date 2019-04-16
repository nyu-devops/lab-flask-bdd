import logging
from flask import Flask

# NOTE: Do not change the order of this code
# The Flask app must be created
# BEFORE you import modules that depend on it !!!

# Create the Flask aoo
app = Flask(__name__)

# Load Configurations
app.config.from_object('config')

import server
import models
import custom_exceptions

# Set up logging for production
print('Setting up logging for {}...'.format(__name__))
if __name__ != '__main__':
    # sync with gunicorn logger
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
