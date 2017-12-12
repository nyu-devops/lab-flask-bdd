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
Order API Service Test Suite

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
class TestOrderServer(unittest.TestCase):
    """ Order Service tests """

    def setUp(self):
        self.app = server.app.test_client()
        server.initialize_logging(logging.CRITICAL)
        server.init_db()
        server.data_reset()
        server.data_load({"name": "fido", "time": "dog", "status": True})
        server.data_load({"name": "kitty", "time": "cat", "status": True})

    def test_index(self):
        """ Test the index page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertIn('Order Demo REST API Service', resp.data)

    def test_get_order_list(self):
        """ Get a list of Orders """
        resp = self.app.get('/orders')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)

    def test_get_order(self):
        """ get a single Order """
        resp = self.app.get('/orders/2')
        #print 'resp_data: ' + resp.data
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'kitty')

    def test_get_order_not_found(self):
        """ Get a Order that doesn't exist """
        resp = self.app.get('/orders/0')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)
        data = json.loads(resp.data)
        self.assertIn('was not found', data['message'])

    def test_create_order(self):
        """ Create a new Order """
        # save the current number of orders for later comparrison
        order_count = self.get_order_count()
        # add a new order
        new_order = {'name': 'sammy', 'time': 'snake', 'status': True}
        data = json.dumps(new_order)
        resp = self.app.post('/orders', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertNotEqual(location, None)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'sammy')
        # check that count has gone up and includes sammy
        resp = self.app.get('/orders')
        # print 'resp_data(2): ' + resp.data
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(len(data), order_count + 1)
        self.assertIn(new_json, data)

    def test_update_order(self):
        """ Update a Order """
        new_kitty = {'name': 'kitty', 'time': 'tabby', 'status': True}
        data = json.dumps(new_kitty)
        resp = self.app.put('/orders/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        resp = self.app.get('/orders/2', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['time'], 'tabby')

    def test_update_order_with_no_name(self):
        """ Update a Order without assigning a name """
        new_order = {'time': 'dog'}
        data = json.dumps(new_order)
        resp = self.app.put('/orders/2', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_update_order_not_found(self):
        """ Update a Order that doesn't exist """
        new_kitty = {"name": "timothy", "time": "mouse"}
        data = json.dumps(new_kitty)
        resp = self.app.put('/orders/0', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

    def test_delete_order(self):
        """ Delete a Order """
        # save the current number of orders for later comparrison
        order_count = self.get_order_count()
        # delete a order
        resp = self.app.delete('/orders/2', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_order_count()
        self.assertEqual(new_count, order_count - 1)

    def test_create_order_with_no_name(self):
        """ Create a Order without a name """
        new_order = {'time': 'dog'}
        data = json.dumps(new_order)
        resp = self.app.post('/orders', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_create_order_no_content_type(self):
        """ Create a Order with no Content-Type """
        new_order = {'time': 'dog'}
        data = json.dumps(new_order)
        resp = self.app.post('/orders', data=data)
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_get_nonexisting_order(self):
        """ Get a nonexisting Order """
        resp = self.app.get('/orders/5')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

    def test_call_create_with_an_id(self):
        """ Call create passing anid """
        new_order = {'name': 'sammy', 'time': 'snake'}
        data = json.dumps(new_order)
        resp = self.app.post('/orders/1', data=data)
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    def test_query_order_list(self):
        """ Query Orders by time """
        resp = self.app.get('/orders', query_string='time=dog')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertIn('fido', resp.data)
        self.assertNotIn('kitty', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['time'], 'dog')

    def test_purchase_a_order(self):
        """ Purchase a Order """
        resp = self.app.put('/orders/2/purchase', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        resp = self.app.get('/orders/2', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        order_data = json.loads(resp.data)
        self.assertEqual(order_data['status'], False)

    def test_purchase_not_status(self):
        """ Purchase a Order that is not status """
        resp = self.app.put('/orders/2/purchase', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        resp = self.app.put('/orders/2/purchase', content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)
        resp_json = json.loads(resp.get_data())
        self.assertIn('not status', resp_json['message'])


######################################################################
# Utility functions
######################################################################

    def get_order_count(self):
        """ save the current number of orders """
        resp = self.app.get('/orders')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
