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
Pet Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color
nosetests --stop tests/test_pets.py:TestPets
"""

import logging
from datetime import date
from unittest import TestCase
from unittest.mock import MagicMock, patch
from requests import HTTPError, ConnectionError
from service.models import Pet, Gender, DataValidationError, DatabaseConnectionError
from tests.factories import PetFactory

# cspell:ignore VCAP SQLDB
VCAP_SERVICES = {
    "cloudantNoSQLDB": [
        {
            "credentials": {
                "username": "admin",
                "password": "pass",
                "host": "localhost",
                "port": 5984,
                "url": "http://admin:pass@localhost:5984",
            }
        }
    ]
}

VCAP_NO_SERVICES = {"noCloudant": []}

BINDING_CLOUDANT = {
    "username": "admin",
    "password": "pass",
    "host": "localhost",
    "port": 5984,
    "url": "http://admin:pass@localhost:5984",
}

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPetModel(TestCase):
    """Test Cases for Pet Model"""

    def setUp(self):
        """Initialize the Cloudant database"""
        Pet.init_db("test")
        Pet.remove_all()

    def _create_pets(self, count: int) -> list:
        """Creates a collection of pets in the database"""
        pet_collection = []
        for _ in range(count):
            pet = PetFactory()
            pet.create()
            pet_collection.append(pet)
        return pet_collection

    def test_create_a_pet(self):
        """Create a pet and assert that it exists"""
        pet = Pet("fido", "dog", False, Gender.MALE, date(2020,4,1))
        self.assertNotEqual(pet, None)
        self.assertEqual(pet.id, None)
        self.assertEqual(pet.name, "fido")
        self.assertEqual(pet.category, "dog")
        self.assertEqual(pet.available, False)
        self.assertEqual(pet.gender, Gender.MALE)
        self.assertEqual(pet.birthday, date(2020,4,1))

    def test_add_a_pet(self):
        """Create a pet and add it to the database"""
        pets = Pet.all()
        self.assertEqual(pets, [])
        pet = PetFactory()
        logging.debug("Pet: %s", pet.serialize())
        self.assertNotEqual(pet, None)
        self.assertEqual(pet.id, None)
        pet.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertNotEqual(pet.id, None)
        pets = Pet.all()
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].name, pet.name)
        self.assertEqual(pets[0].category, pet.category)
        self.assertEqual(pets[0].available, pet.available)
        self.assertEqual(pets[0].gender, pet.gender)
        self.assertEqual(pets[0].birthday, pet.birthday)

    def test_update_a_pet(self):
        """Update a Pet"""
        pet = PetFactory()
        logging.debug("Pet: %s", pet.serialize())
        pet.create()
        self.assertNotEqual(pet.id, None)
        # Change it an save it
        pet.category = "k9"
        pet.update()
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        pets = Pet.all()
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].category, "k9")
        self.assertEqual(pets[0].name, pet.name)

    def test_delete_a_pet(self):
        """Delete a Pet"""
        pet = PetFactory()
        logging.debug("Pet: %s", pet.serialize())
        pet.create()
        self.assertEqual(len(Pet.all()), 1)
        # delete the pet and make sure it isn't in the database
        pet.delete()
        self.assertEqual(len(Pet.all()), 0)

    def test_serialize_a_pet(self):
        """Serialize a Pet"""
        pet = PetFactory()
        data = pet.serialize()
        logging.debug("Pet data: %s", data)
        self.assertNotEqual(data, None)
        self.assertNotIn("_id", data)
        self.assertEqual(data["name"], pet.name)
        self.assertEqual(data["category"], pet.category)
        self.assertEqual(data["available"], pet.available)
        self.assertEqual(data["gender"], pet.gender.name)
        self.assertEqual(data["birthday"], pet.birthday.isoformat())

    def test_deserialize_a_pet(self):
        """Deserialize a Pet"""
        data = PetFactory().serialize()
        logging.debug("Pet data: %s", data)
        pet = Pet()
        pet.deserialize(data)
        self.assertNotEqual(pet, None)
        self.assertEqual(pet.id, None)
        self.assertEqual(pet.name, data["name"])
        self.assertEqual(pet.category, data["category"])
        self.assertEqual(pet.available, data["available"])
        self.assertEqual(pet.gender.name, data["gender"])
        self.assertEqual(pet.birthday, date.fromisoformat(data["birthday"]))

    def test_deserialize_with_no_name(self):
        """Deserialize a Pet that has no name"""
        data = {"id": 0, "category": "cat"}
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_with_no_data(self):
        """Deserialize a Pet that has no data"""
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """Deserialize a Pet that has bad data"""
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, "string data")

    def test_save_a_pet_with_no_name(self):
        """Save a Pet with no name"""
        pet = Pet(None, "cat")
        self.assertRaises(DataValidationError, pet.create)

    def test_create_a_pet_with_no_name(self):
        """Create a Pet with no name"""
        pet = Pet(None, "cat")
        self.assertRaises(DataValidationError, pet.create)

    def test_find_pet(self):
        """Find a Pet by id"""
        pets = self._create_pets(5)
        saved_pet = pets[0]
        pet = Pet.find(saved_pet.id)
        self.assertIsNot(pet, None)
        self.assertEqual(pet.id, saved_pet.id)
        self.assertEqual(pet.name, saved_pet.name)
        self.assertEqual(pet.category, saved_pet.category)
        self.assertEqual(pet.available, saved_pet.available)
        self.assertEqual(pet.gender, saved_pet.gender)
        self.assertEqual(pet.birthday, saved_pet.birthday)

    def test_find_with_no_pets(self):
        """Find a Pet with empty database"""
        pet = Pet.find("foo")
        self.assertIs(pet, None)

    def test_pet_not_found(self):
        """Find a Pet that doesn't exist"""
        PetFactory().create()
        pet = Pet.find("foo")
        self.assertIs(pet, None)

    def test_find_by_name(self):
        """Find a Pet by Name"""
        self._create_pets(5)
        saved_pet = PetFactory()
        saved_pet.name = "Rumpelstiltskin"
        saved_pet.create()
        # search by name
        pets = Pet.find_by_name("Rumpelstiltskin")
        self.assertNotEqual(len(pets), 0)
        pet = pets[0]
        self.assertEqual(pet.name, "Rumpelstiltskin")
        self.assertEqual(pet.category, saved_pet.category)
        self.assertEqual(pet.available, saved_pet.available)
        self.assertEqual(pet.gender, saved_pet.gender)
        self.assertEqual(pet.birthday, saved_pet.birthday)

    def test_find_by_category(self):
        """Find a Pet by Category"""
        pets = self._create_pets(5)
        category = pets[0].category
        category_count =  len([pet for pet in pets if pet.category == category])
        logging.debug("Looking for %d Pets in category %s", category_count, category)
        found_pets = Pet.find_by_category(category)
        self.assertEqual(len(found_pets), category_count)
        for pet in found_pets:
            self.assertEqual(pet.category, category)

    def test_find_by_availability(self):
        """Find a Pet by Availability"""
        pets = self._create_pets(5)
        available = pets[0].available
        available_count = len([pet for pet in pets if pet.available == available])
        logging.debug("Looking for %d Pets where availabe is %s", available_count, available)
        found_pets = Pet.find_by_availability(available)
        self.assertEqual(len(found_pets), available_count)
        for pet in found_pets:
            self.assertEqual(pet.available, available)

    def test_find_by_gender(self):
        """Find a Pet by Gender"""
        pets = self._create_pets(5)
        gender = pets[0].gender
        gender_count =  len([pet for pet in pets if pet.gender == gender])
        logging.debug("Looking for %d Pets where gender is %s", gender_count, gender)
        found_pets = Pet.find_by_gender(gender.name)
        self.assertEqual(len(found_pets), gender_count)
        for pet in found_pets:
            self.assertEqual(pet.gender, gender)

    def test_create_query_index(self):
        """Test create query index"""
        self._create_pets(5)
        Pet.create_query_index("category")

    def test_disconnect(self):
        """Test Disconnet"""
        Pet.disconnect()
        pet = PetFactory()
        self.assertRaises(AttributeError, pet.create)

    @patch("cloudant.database.CloudantDatabase.create_document")
    def test_http_error(self, bad_mock):
        """Test a Bad Create with HTTP error"""
        bad_mock.side_effect = HTTPError()
        pet = PetFactory()
        pet.create()
        self.assertIsNone(pet.id)

    @patch("cloudant.document.Document.exists")
    def test_document_not_exist(self, bad_mock):
        """Test a Bad Document Exists"""
        bad_mock.return_value = False
        pet = PetFactory()
        pet.create()
        self.assertIsNone(pet.id)

    @patch("cloudant.database.CloudantDatabase.__getitem__")
    def test_key_error_on_update(self, bad_mock):
        """Test KeyError on update"""
        bad_mock.side_effect = KeyError()
        pet = PetFactory()
        pet.create()
        pet.name = "Rumpelstiltskin"
        pet.update()

    @patch("cloudant.database.CloudantDatabase.__getitem__")
    def test_key_error_on_delete(self, bad_mock):
        """Test KeyError on delete"""
        bad_mock.side_effect = KeyError()
        pet = PetFactory()
        pet.create()
        pet.delete()

    @patch("cloudant.client.Cloudant.__init__")
    def test_connection_error(self, bad_mock):
        """Test Connection error handler"""
        bad_mock.side_effect = ConnectionError()
        self.assertRaises(DatabaseConnectionError, Pet.init_db, "test")

    # @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES)})
    # def test_vcap_services(self):
    #     """ Test if VCAP_SERVICES works """
    #     Pet.init_db("test")
    #     self.assertIsNotNone(Pet.client)
    #
