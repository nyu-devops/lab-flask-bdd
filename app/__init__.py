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
