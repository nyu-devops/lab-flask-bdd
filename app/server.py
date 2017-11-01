######################################################################
# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
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
Pet Store Service with UI

Paths:
------
GET / - Displays a UI for Selenium testing
GET /pets - Returns a list all of the Pets
GET /pets/{id} - Returns the Pet with a given id number
POST /pets - creates a new Pet record in the database
PUT /pets/{id} - updates a Pet record in the database
DELETE /pets/{id} - deletes a Pet record in the database
"""

import sys
import logging
from flask import jsonify, request, json, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from app.models import Pet
from . import app

# Error handlers reuire app to be initialized so we must import
# then only after we have initialized the Flask app instance
import error_handlers

######################################################################
# GET HEALTH CHECK
######################################################################
@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200, message='Healthy'), status.HTTP_200_OK)

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    # data = '{name: <string>, category: <string>}'
    # url = request.base_url + 'pets' # url_for('list_pets')
    # return jsonify(name='Pet Demo REST API Service', version='1.0', url=url, data=data), status.HTTP_200_OK
    return app.send_static_file('index.html')

######################################################################
# LIST ALL PETS
######################################################################
@app.route('/pets', methods=['GET'])
def list_pets():
    """ Returns all of the Pets """
    pets = []
    category = request.args.get('category')
    name = request.args.get('name')
    if category:
        pets = Pet.find_by_category(category)
    elif name:
        pets = Pet.find_by_name(name)
    else:
        pets = Pet.all()

    results = [pet.serialize() for pet in pets]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE A PET
######################################################################
@app.route('/pets/<int:pet_id>', methods=['GET'])
def get_pets(pet_id):
    """
    Retrieve a single Pet

    This endpoint will return a Pet based on it's id
    """
    pet = Pet.find(pet_id)
    if not pet:
        raise NotFound("Pet with id '{}' was not found.".format(pet_id))
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW PET
######################################################################
@app.route('/pets', methods=['POST'])
def create_pets():
    """
    Creates a Pet
    This endpoint will create a Pet based the data in the body that is posted
    """
    data = {}
    # Check for form submission data
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        data = {
            'name': request.form['name'],
            'category': request.form['category'],
            'available': True
        }
    else:
        data = request.get_json()
    pet = Pet()
    pet.deserialize(data)
    pet.save()
    message = pet.serialize()
    location_url = url_for('get_pets', pet_id=pet.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {'Location': location_url})


######################################################################
# UPDATE AN EXISTING PET
######################################################################
@app.route('/pets/<int:pet_id>', methods=['PUT'])
def update_pets(pet_id):
    """
    Update a Pet

    This endpoint will update a Pet based the body that is posted
    """
    check_content_type('application/json')
    pet = Pet.find(pet_id)
    if not pet:
        raise NotFound("Pet with id '{}' was not found.".format(pet_id))
    pet.deserialize(request.get_json())
    pet.id = pet_id
    pet.save()
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A PET
######################################################################
@app.route('/pets/<int:pet_id>', methods=['DELETE'])
def delete_pets(pet_id):
    """
    Delete a Pet

    This endpoint will delete a Pet based the id specified in the path
    """
    pet = Pet.find(pet_id)
    if pet:
        pet.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# PURCHASE A PET
######################################################################
@app.route('/pets/<int:pet_id>/purchase', methods=['PUT'])
def purchase_pets(pet_id):
    """ Purchasing a Pet makes it unavailable """
    pet = Pet.find(pet_id)
    if not pet:
        abort(status.HTTP_404_NOT_FOUND, "Pet with id '{}' was not found.".format(pet_id))
    if not pet.available:
        abort(status.HTTP_400_BAD_REQUEST, "Pet with id '{}' is not available.".format(pet_id))
    pet.available = False
    pet.save()
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE ALL PET DATA (for testing only)
######################################################################
# @app.route('/pets/reset', methods=['DELETE'])
# def pets_reset():
#     redis.flushall()

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

@app.before_first_request
def init_db(redis=None):
    """ Initlaize the model """
    Pet.init_db(redis)

# load sample data
def data_load(payload):
    """ Loads a Pet into the database """
    pet = Pet(0, payload['name'], payload['category'])
    pet.save()

def data_reset():
    """ Removes all Pets from the database """
    Pet.remove_all()

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Content-Type must be {}'.format(content_type))

#@app.before_first_request
def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')
