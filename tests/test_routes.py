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

"""
Pet API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_service.py:TestPetService
"""
import os
from unittest import TestCase
import logging
from urllib.parse import quote_plus
from werkzeug.datastructures import MultiDict, ImmutableMultiDict
from service import app
from service.utils import status
from service.models import db, init_db, Pet, Gender
from tests.factories import PetFactory

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
# logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/pets"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestPetRoutes(TestCase):
    """Pet Service tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Pet).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    ############################################################
    # Utility function to bulk create pets
    ############################################################
    def _create_pets(self, count: int = 1) -> list:
        """Factory method to create pets in bulk"""
        pets = []
        for _ in range(count):
            test_pet = PetFactory()
            response = self.client.post(BASE_URL, json=test_pet.serialize())
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test pet"
            )
            new_pet = response.get_json()
            test_pet.id = new_pet["id"]
            pets.append(test_pet)
        return pets

    ############################################################
    #  T E S T   C A S E S
    ############################################################
    def test_index(self):
        """It should return the index page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"Pet Demo REST API Service", resp.data)

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------
    def test_get_pet_list(self):
        """It should Get a list of Pets"""
        self._create_pets(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_pet(self):
        """It should Get a single Pet"""
        # get the id of a pet
        test_pet = self._create_pets(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_pet.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_pet.name)

    def test_get_pet_not_found(self):
        """It should not Get a Pet thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_pet(self):
        """It should Create a new Pet"""
        test_pet = PetFactory()
        logging.debug("Test Pet: %s", test_pet.serialize())
        response = self.client.post(BASE_URL, json=test_pet.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_pet = response.get_json()
        self.assertEqual(new_pet["name"], test_pet.name)
        self.assertEqual(new_pet["category"], test_pet.category)
        self.assertEqual(new_pet["available"], test_pet.available)
        self.assertEqual(new_pet["gender"], test_pet.gender.name)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_pet = response.get_json()
        self.assertEqual(new_pet["name"], test_pet.name)
        self.assertEqual(new_pet["category"], test_pet.category)
        self.assertEqual(new_pet["available"], test_pet.available)
        self.assertEqual(new_pet["gender"], test_pet.gender.name)

    def test_create_pet_from_formdata(self):
        """It should process FORM data"""
        pet = PetFactory().serialize()
        pet_data = MultiDict()
        pet_data.add("name", pet["name"])
        pet_data.add("category", pet["category"])
        pet_data.add("available", pet["available"])
        pet_data.add("gender", pet["gender"])
        pet_data.add("birthday", pet["birthday"])
        data = ImmutableMultiDict(pet_data)
        logging.debug("Sending Pet data: %s", data)
        resp = self.client.post(BASE_URL, data=data, content_type="application/x-www-form-urlencoded")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertNotEqual(location, None)
        # Check the data is correct
        data = resp.get_json()
        logging.debug("data = %s", data)
        self.assertEqual(data["name"], pet["name"])

    def test_create_pet_with_no_name(self):
        """It should not Create a Pet without a name"""
        pet = self._create_pets()[0]
        new_pet = pet.serialize()
        del new_pet["name"]
        logging.debug("Pet no name: %s", new_pet)
        resp = self.client.post(BASE_URL, json=new_pet)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_pet_no_content_type(self):
        """It should not Create a Pet with no Content-Type"""
        resp = self.client.post(BASE_URL, data="bad data")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_pet_wrong_content_type(self):
        """It should not Create a Pet with wrong Content-Type"""
        resp = self.client.post(BASE_URL, data={}, content_type="plain/text")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_call_create_with_an_id(self):
        """It should not allow calling endpoint incorrectly"""
        resp = self.client.post(f"{BASE_URL}/0", json={})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_pet(self):
        """It should Update an existing Pet"""
        # create a pet to update
        test_pet = PetFactory()
        response = self.client.post(BASE_URL, json=test_pet.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the pet
        new_pet = response.get_json()
        logging.debug(new_pet)
        new_pet["category"] = "unknown"
        response = self.client.put(f"{BASE_URL}/{new_pet['id']}", json=new_pet)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_pet = response.get_json()
        self.assertEqual(updated_pet["category"], "unknown")

    def test_update_pet_with_no_name(self):
        """It should not Update a Pet without assigning a name"""
        pet = self._create_pets()[0]
        pet_data = pet.serialize()
        del pet_data["name"]
        resp = self.client.put(
            f"{BASE_URL}/{pet.id}",
            json=pet_data,
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_pet_not_found(self):
        """It should not Update a Pet that doesn't exist"""
        resp = self.client.put(f"{BASE_URL}/foo", json={}, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_pet(self):
        """It should Delete a Pet"""
        pets = self._create_pets(5)
        pet_count = self.get_pet_count()
        test_pet = pets[0]
        resp = self.client.delete(f"{BASE_URL}/{test_pet.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.client.get(f"{BASE_URL}/{test_pet.id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        new_count = self.get_pet_count()
        self.assertEqual(new_count, pet_count - 1)

    def test_delete_non_existing_pet(self):
        """It should Delete a Pet even if it doesn't exist"""
        resp = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------
    def test_query_by_name(self):
        """It should Query Pets by name"""
        pets = self._create_pets(5)
        test_name = pets[0].name
        name_count = len([pet for pet in pets if pet.name == test_name])
        resp = self.client.get(
            BASE_URL, query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), name_count)
        # check the data just to be sure
        for pet in data:
            self.assertEqual(pet["name"], test_name)

    def test_query_pet_list_by_category(self):
        """It should Query Pets by Category"""
        pets = self._create_pets(10)
        test_category = pets[0].category
        category_pets = [pet for pet in pets if pet.category == test_category]
        response = self.client.get(
            BASE_URL,
            query_string=f"category={quote_plus(test_category)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), len(category_pets))
        # check the data just to be sure
        for pet in data:
            self.assertEqual(pet["category"], test_category)

    def test_query_by_availability(self):
        """It should Query Pets by availability"""
        pets = self._create_pets(10)
        available_pets = [pet for pet in pets if pet.available is True]
        unavailable_pets = [pet for pet in pets if pet.available is False]
        available_count = len(available_pets)
        unavailable_count = len(unavailable_pets)
        logging.debug("Available Pets [%d] %s", available_count, available_pets)
        logging.debug("Unavailable Pets [%d] %s", unavailable_count, unavailable_pets)

        # test for available
        resp = self.client.get(
            BASE_URL, query_string="available=true"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), available_count)
        # check the data just to be sure
        for pet in data:
            self.assertEqual(pet["available"], True)

        # test for unavailable
        resp = self.client.get(
            BASE_URL, query_string="available=false"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), unavailable_count)
        # check the data just to be sure
        for pet in data:
            self.assertEqual(pet["available"], False)

    def test_query_by_gender(self):
        """It should Query Pets by gender"""
        pets = self._create_pets(10)
        female_pets = [pet for pet in pets if pet.gender == Gender.FEMALE]
        female_count = len(female_pets)
        logging.debug("Female Pets [%d] %s", female_count, female_pets)

        # test for available
        resp = self.client.get(
            BASE_URL, query_string="gender=female"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), female_count)
        # check the data just to be sure
        for pet in data:
            self.assertEqual(pet["gender"], Gender.FEMALE.name)

    # ----------------------------------------------------------
    # TEST ACTION
    # ----------------------------------------------------------
    def test_purchase_a_pet(self):
        """It should Purchase a Pet"""
        pets = self._create_pets(10)
        available_pets = [pet for pet in pets if pet.available is True]
        pet = available_pets[0]
        resp = self.client.put(f"{BASE_URL}/{pet.id}/purchase", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.get(f"{BASE_URL}/{pet.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        logging.debug("Response data: %s", data)
        self.assertEqual(data["available"], False)

    def test_purchase_not_available(self):
        """It should not Purchase a Pet that is not available"""
        pets = self._create_pets(10)
        unavailable_pets = [pet for pet in pets if pet.available is False]
        pet = unavailable_pets[0]
        resp = self.client.put(f"{BASE_URL}/{pet.id}/purchase", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    ######################################################################
    # Utility functions
    ######################################################################

    def get_pet_count(self):
        """save the current number of pets"""
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        # logging.debug("data = %s", data)
        return len(data)
