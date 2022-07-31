######################################################################
# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
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

# spell: ignore Rofrano jsonify restx dbname
"""
Pet Store Service with UI
"""
from flask import jsonify, request, url_for, make_response, abort
from service.models import Pet, Gender
from service.utils import status  # HTTP Status Codes
from . import app


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def healthcheck():
    """Let them know our heart is still beating"""
    return make_response(jsonify(status=200, message="OK"), status.HTTP_200_OK)


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
# LIST ALL PETS
######################################################################
@app.route("/pets", methods=["GET"])
def list_pets():
    """Returns all of the Pets"""
    app.logger.info("Request to list Pets...")

    pets = []
    category = request.args.get("category")
    name = request.args.get("name")
    available = request.args.get("available")
    gender = request.args.get("gender")

    if category:
        app.logger.info("Find by category: %s", category)
        pets = Pet.find_by_category(category)
    elif name:
        app.logger.info("Find by name: %s", name)
        pets = Pet.find_by_name(name)
    elif available:
        app.logger.info("Find by available: %s", available)
        # create bool from string
        available_value = available.lower() in ["true", "yes", "1"]
        pets = Pet.find_by_availability(available_value)
    elif gender:
        app.logger.info("Find by gender: %s", gender)
        # create enum from string
        gender_value = getattr(Gender, gender.upper())
        pets = Pet.find_by_gender(gender_value)
    else:
        app.logger.info("Find all")
        pets = Pet.all()

    results = [pet.serialize() for pet in pets]
    app.logger.info("[%s] Pets returned", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE A PET
######################################################################
@app.route("/pets/<int:pet_id>", methods=["GET"])
def get_pets(pet_id):
    """
    Retrieve a single Pet

    This endpoint will return a Pet based on it's id
    """
    app.logger.info("Request to Retrieve a pet with id [%s]", pet_id)

    pet = Pet.find(pet_id)
    if not pet:
        abort(status.HTTP_404_NOT_FOUND, f"Pet with id '{pet_id}' was not found.")

    app.logger.info("Returning pet: %s", pet.name)
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)


######################################################################
# CREATE A NEW PET
######################################################################
@app.route("/pets", methods=["POST"])
def create_pets():
    """
    Creates a Pet
    This endpoint will create a Pet based the data in the body that is posted
    """
    app.logger.info("Request to Create a Pet...")
    data = {}
    # Check for form submission data
    if request.headers.get("Content-Type") == "application/x-www-form-urlencoded":
        app.logger.info("Getting data from FORM submit")
        data = {
            "name": request.form["name"],
            "category": request.form["category"],
            "available": request.form["available"] in ['True', 'true', '1'],
            "gender": request.form["gender"],
            "birthday": request.form["birthday"]
        }
    else:
        check_content_type("application/json")
        app.logger.info("Getting json data from API call")
        data = request.get_json()

    app.logger.info("Processing: %s", data)
    pet = Pet()
    pet.deserialize(data)
    pet.create()
    app.logger.info("Pet with new id [%s] saved!", pet.id)

    message = pet.serialize()
    location_url = url_for("get_pets", pet_id=pet.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED, {"Location": location_url})


######################################################################
# UPDATE AN EXISTING PET
######################################################################
@app.route("/pets/<int:pet_id>", methods=["PUT"])
def update_pets(pet_id):
    """
    Update a Pet

    This endpoint will update a Pet based the body that is posted
    """
    app.logger.info("Request to Update a pet with id [%s]", pet_id)
    check_content_type("application/json")

    pet = Pet.find(pet_id)
    if not pet:
        abort(status.HTTP_404_NOT_FOUND, f"Pet with id '{pet_id}' was not found.")

    data = request.get_json()
    app.logger.info(data)
    pet.deserialize(data)
    pet.id = pet_id
    pet.update()
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE A PET
######################################################################
@app.route("/pets/<int:pet_id>", methods=["DELETE"])
def delete_pets(pet_id):
    """
    Delete a Pet

    This endpoint will delete a Pet based the id specified in the path
    """
    app.logger.info("Request to Delete a pet with id [%s]", pet_id)

    pet = Pet.find(pet_id)
    if pet:
        pet.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# PURCHASE A PET
######################################################################
@app.route("/pets/<int:pet_id>/purchase", methods=["PUT"])
def purchase_pets(pet_id):
    """Purchasing a Pet makes it unavailable"""
    pet = Pet.find(pet_id)
    if not pet:
        abort(status.HTTP_404_NOT_FOUND, f"Pet with id '{pet_id}' was not found.")
    if not pet.available:
        abort(
            status.HTTP_409_CONFLICT,
            f"Pet with id '{pet_id}' is not available.",
        )
    pet.available = False
    pet.update()
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
