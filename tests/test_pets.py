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

"""
Pet Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color
"""

import unittest
import os
import json
from mock import patch
from redis import Redis, ConnectionError
from werkzeug.exceptions import NotFound
from app.models import Pet
from app.custom_exceptions import DataValidationError
from app import server  # to get Redis

VCAP_SERVICES = os.getenv('VCAP_SERVICES', None)
if not VCAP_SERVICES:
    VCAP_SERVICES = {
        "rediscloud": [
            {"credentials": {
                "password": None,
                "hostname": "127.0.0.1",
                "port": "6379"
                }
            }
        ]
    }


######################################################################
#  T E S T   C A S E S
######################################################################
class TestPets(unittest.TestCase):
    """ Test Cases for Pet Model """

    def setUp(self):
        """ Initialize the Redis database """
        Pet.init_db()
        Pet.remove_all()

    def test_create_a_pet(self):
        """ Create a pet and assert that it exists """
        pet = Pet(0, "fido", "dog", False)
        self.assertNotEqual(pet, None)
        self.assertEqual(pet.id, 0)
        self.assertEqual(pet.name, "fido")
        self.assertEqual(pet.category, "dog")
        self.assertEqual(pet.available, False)

    def test_add_a_pet(self):
        """ Create a pet and add it to the database """
        pets = Pet.all()
        self.assertEqual(pets, [])
        pet = Pet(0, "fido", "dog", True)
        self.assertTrue(pet != None)
        self.assertEqual(pet.id, 0)
        pet.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(pet.id, 1)
        pets = Pet.all()
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].id, 1)
        self.assertEqual(pets[0].name, "fido")
        self.assertEqual(pets[0].category, "dog")
        self.assertEqual(pets[0].available, True)

    def test_update_a_pet(self):
        """ Update a Pet """
        pet = Pet(0, "fido", "dog", True)
        pet.save()
        self.assertEqual(pet.id, 1)
        # Change it an save it
        pet.category = "k9"
        pet.save()
        self.assertEqual(pet.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        pets = Pet.all()
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].category, "k9")
        self.assertEqual(pets[0].name, "fido")

    def test_delete_a_pet(self):
        """ Delete a Pet """
        pet = Pet(0, "fido", "dog")
        pet.save()
        self.assertEqual(len(Pet.all()), 1)
        # delete the pet and make sure it isn't in the database
        pet.delete()
        self.assertEqual(len(Pet.all()), 0)

    def test_serialize_a_pet(self):
        """ Serialize a Pet """
        pet = Pet(0, "fido", "dog")
        data = pet.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], 0)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "fido")
        self.assertIn('category', data)
        self.assertEqual(data['category'], "dog")

    def test_deserialize_a_pet(self):
        """ Deserialize a Pet """
        data = {"id":1, "name": "kitty", "category": "cat", "available": True}
        pet = Pet(data['id'])
        pet.deserialize(data)
        self.assertNotEqual(pet, None)
        self.assertEqual(pet.id, 1)
        self.assertEqual(pet.name, "kitty")
        self.assertEqual(pet.category, "cat")

    def test_deserialize_with_no_name(self):
        """ Deserialize a Pet that has no name """
        data = {"id":0, "category": "cat"}
        pet = Pet(0)
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Pet that has no data """
        pet = Pet(0)
        self.assertRaises(DataValidationError, pet.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserialize a Pet that has bad data """
        pet = Pet(0)
        self.assertRaises(DataValidationError, pet.deserialize, "string data")

    def test_save_a_pet_with_no_name(self):
        """ Save a Pet with no name """
        pet = Pet(0, None, "cat")
        self.assertRaises(DataValidationError, pet.save)

    def test_find_pet(self):
        """ Find a Pet by id """
        Pet(0, "fido", "dog").save()
        Pet(0, "kitty", "cat").save()
        pet = Pet.find(2)
        self.assertIsNot(pet, None)
        self.assertEqual(pet.id, 2)
        self.assertEqual(pet.name, "kitty")

    def test_find_with_no_pets(self):
        """ Find a Pet with empty database """
        pet = Pet.find(1)
        self.assertIs(pet, None)

    def test_pet_not_found(self):
        """ Find a Pet that doesnt exist """
        Pet(0, "fido", "dog").save()
        pet = Pet.find(2)
        self.assertIs(pet, None)

    def test_find_by_name(self):
        """ Find a Pet by Name """
        Pet(0, "fido", "dog").save()
        Pet(0, "kitty", "cat").save()
        pets = Pet.find_by_name("fido")
        self.assertNotEqual(len(pets), 0)
        self.assertEqual(pets[0].category, "dog")
        self.assertEqual(pets[0].name, "fido")

    def test_find_by_category(self):
        """ Find a Pet by Category """
        Pet(0, "fido", "dog").save()
        Pet(0, "kitty", "cat").save()
        pets = Pet.find_by_category("cat")
        self.assertNotEqual(len(pets), 0)
        self.assertEqual(pets[0].category, "cat")
        self.assertEqual(pets[0].name, "kitty")

    def test_find_by_availability(self):
        """ Find a Pet by Availability """
        Pet(0, "fido", "dog", False).save()
        Pet(0, "kitty", "cat", True).save()
        pets = Pet.find_by_availability(True)
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].name, "kitty")

    def test_for_case_insensitive(self):
        """ Test for Case Insensitive Search """
        Pet(0, "Fido", "DOG").save()
        Pet(0, "Kitty", "CAT").save()
        pets = Pet.find_by_name("fido")
        self.assertNotEqual(len(pets), 0)
        self.assertEqual(pets[0].name, "Fido")
        pets = Pet.find_by_category("cat")
        self.assertNotEqual(len(pets), 0)
        self.assertEqual(pets[0].category, "CAT")

    @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES)})
    def test_vcap_services(self):
        """ Test if VCAP_SERVICES works """
        Pet.init_db()
        self.assertIsNotNone(Pet.redis)

    @patch('redis.Redis.ping')
    def test_redis_connection_error(self, ping_error_mock):
        """ Test a Bad Redis connection """
        ping_error_mock.side_effect = ConnectionError()
        self.assertRaises(ConnectionError, Pet.init_db)
        self.assertIsNone(Pet.redis)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestPets)
    # unittest.TextTestRunner(verbosity=2).run(suite)
