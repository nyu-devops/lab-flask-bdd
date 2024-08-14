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
Pet Store Service with Swagger

Paths:
------
GET / - Displays a UI for Selenium testing
GET /pets - Returns a list all of the Pets
GET /pets/{id} - Returns the Pet with a given id number
POST /pets - creates a new Pet record in the database
PUT /pets/{id} - updates a Pet record in the database
DELETE /pets/{id} - deletes a Pet record in the database
"""

import secrets
from functools import wraps
from flask import request
from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse, inputs
from service.models import Pet, Gender
from service.common import status  # HTTP Status Codes
from . import api


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """Index page"""
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Pet",
    {
        "name": fields.String(required=True, description="The name of the Pet"),
        "category": fields.String(
            required=True,
            description="The category of Pet (e.g., dog, cat, fish, etc.)",
        ),
        "available": fields.Boolean(
            required=True, description="Is the Pet available for purchase?"
        ),
        # pylint: disable=protected-access
        "gender": fields.String(
            enum=Gender._member_names_, description="The gender of the Pet"
        ),
        "birthday": fields.Date(required=True, description="The day the pet was born"),
    },
)

pet_model = api.inherit(
    "PetModel",
    create_model,
    {
        "_id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

# query string arguments
pet_args = reqparse.RequestParser()
pet_args.add_argument(
    "name", type=str, location="args", required=False, help="List Pets by name"
)
pet_args.add_argument(
    "category", type=str, location="args", required=False, help="List Pets by category"
)
pet_args.add_argument(
    "available",
    type=inputs.boolean,
    location="args",
    required=False,
    help="List Pets by availability",
)


######################################################################
#  PATH: /pets/{id}
######################################################################
@api.route("/pets/<pet_id>")
@api.param("pet_id", "The Pet identifier")
class PetResource(Resource):
    """
    PetResource class

    Allows the manipulation of a single Pet
    GET /pet{id} - Returns a Pet with the id
    PUT /pet{id} - Update a Pet with the id
    DELETE /pet{id} -  Deletes a Pet with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PET
    # ------------------------------------------------------------------
    @api.doc("get_pets")
    @api.response(404, "Pet not found")
    @api.marshal_with(pet_model)
    def get(self, pet_id):
        """
        Retrieve a single Pet

        This endpoint will return a Pet based on it's id
        """
        app.logger.info("Request to Retrieve a pet with id [%s]", pet_id)
        pet = Pet.find(pet_id)
        if not pet:
            abort(status.HTTP_404_NOT_FOUND, f"Pet with id '{pet_id}' was not found.")
        return pet.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PET
    # ------------------------------------------------------------------
    @api.doc("update_pets")
    @api.response(404, "Pet not found")
    @api.response(400, "The posted Pet data was not valid")
    @api.expect(pet_model)
    @api.marshal_with(pet_model)
    def put(self, pet_id):
        """
        Update a Pet

        This endpoint will update a Pet based the body that is posted
        """
        app.logger.info("Request to Update a pet with id [%s]", pet_id)
        pet = Pet.find(pet_id)
        if not pet:
            abort(status.HTTP_404_NOT_FOUND, f"Pet with id '{pet_id}' was not found.")
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        pet.deserialize(data)
        pet.id = pet_id
        pet.update()
        return pet.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PET
    # ------------------------------------------------------------------
    @api.doc("delete_pets")
    @api.response(204, "Pet deleted")
    def delete(self, pet_id):
        """
        Delete a Pet

        This endpoint will delete a Pet based the id specified in the path
        """
        app.logger.info("Request to Delete a pet with id [%s]", pet_id)
        pet = Pet.find(pet_id)
        if pet:
            pet.delete()
            app.logger.info("Pet with id [%s] was deleted", pet_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /pets
######################################################################
@api.route("/pets", strict_slashes=False)
class PetCollection(Resource):
    """Handles all interactions with collections of Pets"""

    # ------------------------------------------------------------------
    # LIST ALL PETS
    # ------------------------------------------------------------------
    @api.doc("list_pets")
    @api.expect(pet_args, validate=True)
    @api.marshal_list_with(pet_model)
    def get(self):
        """Returns all of the Pets"""
        app.logger.info("Request to list Pets...")
        pets = []
        args = pet_args.parse_args()
        if args["category"]:
            app.logger.info("Filtering by category: %s", args["category"])
            pets = Pet.find_by_category(args["category"])
        elif args["name"]:
            app.logger.info("Filtering by name: %s", args["name"])
            pets = Pet.find_by_name(args["name"])
        elif args["available"] is not None:
            app.logger.info("Filtering by availability: %s", args["available"])
            pets = Pet.find_by_availability(args["available"])
        else:
            app.logger.info("Returning unfiltered list.")
            pets = Pet.all()

        app.logger.info("[%s] Pets returned", len(pets))
        results = [pet.serialize() for pet in pets]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PET
    # ------------------------------------------------------------------
    @api.doc("create_pets")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(pet_model, code=201)
    def post(self):
        """
        Creates a Pet
        This endpoint will create a Pet based the data in the body that is posted
        """
        app.logger.info("Request to Create a Pet")
        pet = Pet()
        app.logger.debug("Payload = %s", api.payload)
        pet.deserialize(api.payload)
        pet.create()
        app.logger.info("Pet with new id [%s] created!", pet.id)
        location_url = api.url_for(PetResource, pet_id=pet.id, _external=True)
        return pet.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

    # ------------------------------------------------------------------
    # DELETE ALL PETS (for testing only)
    # ------------------------------------------------------------------
    @api.doc("delete_all_pets")
    @api.response(204, "All Pets deleted")
    def delete(self):
        """
        Delete all Pet

        This endpoint will delete all Pet only if the system is under test
        """
        app.logger.info("Request to Delete all pets...")
        if "TESTING" in app.config and app.config["TESTING"]:
            Pet.remove_all()
            app.logger.info("Removed all Pets from the database")
        else:
            app.logger.warning("Request to clear database while system not under test")

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /pets/{id}/purchase
######################################################################
@api.route("/pets/<pet_id>/purchase")
@api.param("pet_id", "The Pet identifier")
class PurchaseResource(Resource):
    """Purchase actions on a Pet"""

    @api.doc("purchase_pets")
    @api.response(404, "Pet not found")
    @api.response(409, "The Pet is not available for purchase")
    def put(self, pet_id):
        """
        Purchase a Pet

        This endpoint will purchase a Pet and make it unavailable
        """
        app.logger.info("Request to Purchase a Pet")
        pet = Pet.find(pet_id)
        if not pet:
            abort(status.HTTP_404_NOT_FOUND, f"Pet with id [{pet_id}] was not found.")
        if not pet.available:
            abort(status.HTTP_409_CONFLICT, f"Pet with id [{pet_id}] is not available.")
        pet.available = False
        pet.update()
        app.logger.info("Pet with id [%s] has been purchased!", pet.id)
        return pet.serialize(), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)


def data_reset():
    """Removes all Pets from the database"""
    Pet.remove_all()