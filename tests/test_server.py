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
Pet API Service Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color
"""

import unittest
import logging
import json
from app import server

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPetServer(unittest.TestCase):
    """ Pet Service tests """

    def setUp(self):
        self.app = server.app.test_client()
        server.initialize_logging(logging.CRITICAL)
        server.init_db()
        server.data_reset()
        server.data_load({"name": "fido", "category": "dog", "available": True})
        server.data_load({"name": "kitty", "category": "cat", "available": True})

    def test_index(self):
        """ Test the index page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertIn('Pet Demo REST API Service', resp.data)

    def test_get_pet_list(self):
        """ Get a list of Pets """
        resp = self.app.get('/pets')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)

    def test_get_pet(self):
        """ get a single Pet """
        resp = self.app.get('/pets/2')
        #print 'resp_data: ' + resp.data
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'kitty')

    def test_get_pet_not_found(self):
        """ Get a Pet that doesn't exist """
        resp = self.app.get('/pets/0')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)
        data = json.loads(resp.data)
        self.assertIn('was not found', data['message'])

    def test_create_pet(self):
        """ Create a new Pet """
        # save the current number of pets for later comparrison
        pet_count = self.get_pet_count()
        # add a new pet
        new_pet = {'name': 'sammy', 'category': 'snake', 'available': True}
        data = json.dumps(new_pet)
        resp = self.app.post('/pets', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertNotEqual(location, None)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'sammy')
        # check that count has gone up and includes sammy
        resp = self.app.get('/pets')
        # print 'resp_data(2): ' + resp.data
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(len(data), pet_count + 1)
        self.assertIn(new_json, data)

    def test_update_pet(self):
        """ Update a Pet """
        new_kitty = {'name': 'kitty', 'category': 'tabby', 'available': True}
        data = json.dumps(new_kitty)
        resp = self.app.put('/pets/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        resp = self.app.get('/pets/2', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['category'], 'tabby')

    def test_update_pet_with_no_name(self):
        """ Update a Pet without assigning a name """
        new_pet = {'category': 'dog'}
        data = json.dumps(new_pet)
        resp = self.app.put('/pets/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_update_pet_not_found(self):
        """ Update a Pet that doesn't exist """
        new_kitty = {"name": "timothy", "category": "mouse"}
        data = json.dumps(new_kitty)
        resp = self.app.put('/pets/0', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

    def test_delete_pet(self):
        """ Delete a Pet """
        # save the current number of pets for later comparrison
        pet_count = self.get_pet_count()
        # delete a pet
        resp = self.app.delete('/pets/2', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_pet_count()
        self.assertEqual(new_count, pet_count - 1)

    def test_create_pet_with_no_name(self):
        """ Create a Pet without a name """
        new_pet = {'category': 'dog'}
        data = json.dumps(new_pet)
        resp = self.app.post('/pets', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_create_pet_no_content_type(self):
        """ Create a Pet with no Content-Type """
        new_pet = {'category': 'dog'}
        data = json.dumps(new_pet)
        resp = self.app.post('/pets', data=data)
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_get_nonexisting_pet(self):
        """ Get a nonexisting Pet """
        resp = self.app.get('/pets/5')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

    def test_call_create_with_an_id(self):
        """ Call create passing anid """
        new_pet = {'name': 'sammy', 'category': 'snake'}
        data = json.dumps(new_pet)
        resp = self.app.post('/pets/1', data=data)
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    def test_query_pet_list(self):
        """ Query Pets by category """
        resp = self.app.get('/pets', query_string='category=dog')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertIn('fido', resp.data)
        self.assertNotIn('kitty', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['category'], 'dog')

    def test_purchase_a_pet(self):
        """ Purchase a Pet """
        resp = self.app.put('/pets/2/purchase', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        resp = self.app.get('/pets/2', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        pet_data = json.loads(resp.data)
        self.assertEqual(pet_data['available'], False)

    def test_purchase_not_available(self):
        """ Purchase a Pet that is not available """
        resp = self.app.put('/pets/2/purchase', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        resp = self.app.put('/pets/2/purchase', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)
        resp_json = json.loads(resp.get_data())
        self.assertIn('not available', resp_json['message'])


######################################################################
# Utility functions
######################################################################

    def get_pet_count(self):
        """ save the current number of pets """
        resp = self.app.get('/pets')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
