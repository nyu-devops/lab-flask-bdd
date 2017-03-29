from flask import Flask

# Create the Flask aoo
app = Flask(__name__)

# Load Configurations
app.config.from_object('config')

import server
import pet
import custom_exceptions
