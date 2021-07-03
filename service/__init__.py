######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Package: service

Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import logging
from flask import Flask
from .utils import log_handlers

# NOTE: Do not change the order of this code
# The Flask app must be created
# BEFORE you import modules that depend on it !!!

# Create the Flask aoo
app = Flask(__name__)  # pylint: disable=invalid-name

# Load Configurations
app.config.from_object("config")

# Dependencis rquire we import the routes AFTER the Flask app is created
from service import (
    routes,
    models,
)  # pylint: disable=wrong-import-position, wrong-import-order
from .utils import error_handlers  # pylint: disable=wrong-import-position

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  P E T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

app.logger.info("Service inititalized!")
