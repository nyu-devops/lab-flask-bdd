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
Order Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color
"""

import unittest
import os
import json
from mock import patch
from redis import Redis, ConnectionError
from werkzeug.exceptions import NotFound
from app.models import Order
from app.custom_exceptions import DataValidationError
from app import server  # to get Redis

VCAP_SERVICES = os.getenv('VCAP_SERVICES', None)
if not VCAP_SERVICES:
    VCAP_SERVICES = '{"rediscloud": [{"credentials": {' \
        '"password": "", "hostname": "127.0.0.1", "port": "6379"}}]}'


######################################################################
#  T E S T   C A S E S
######################################################################
class TestOrders(unittest.TestCase):
    """ Test Cases for Order Model """

    def setUp(self):
        """ Initialize the Redis database """
        Order.init_db()
        Order.remove_all()

    def test_create_a_order(self):
        """ Create a order and assert that it exists """
        order = Order(0, "fido", "dog", False)
        self.assertNotEqual(order, None)
        self.assertEqual(order.id, 0)
        self.assertEqual(order.name, "fido")
        self.assertEqual(order.time, "dog")
        self.assertEqual(order.status, False)

    def test_add_a_order(self):
        """ Create a order and add it to the database """
        orders = Order.all()
        self.assertEqual(orders, [])
        order = Order(0, "fido", "dog", True)
        self.assertTrue(order != None)
        self.assertEqual(order.id, 0)
        order.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(order.id, 1)
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].id, 1)
        self.assertEqual(orders[0].name, "fido")
        self.assertEqual(orders[0].time, "dog")
        self.assertEqual(orders[0].status, True)

    def test_update_a_order(self):
        """ Update a Order """
        order = Order(0, "fido", "dog", True)
        order.save()
        self.assertEqual(order.id, 1)
        # Change it an save it
        order.time = "k9"
        order.save()
        self.assertEqual(order.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].time, "k9")
        self.assertEqual(orders[0].name, "fido")

    def test_delete_a_order(self):
        """ Delete a Order """
        order = Order(0, "fido", "dog")
        order.save()
        self.assertEqual(len(Order.all()), 1)
        # delete the order and make sure it isn't in the database
        order.delete()
        self.assertEqual(len(Order.all()), 0)

    def test_serialize_a_order(self):
        """ Serialize a Order """
        order = Order(0, "fido", "dog")
        data = order.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], 0)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "fido")
        self.assertIn('time', data)
        self.assertEqual(data['time'], "dog")

    def test_deserialize_a_order(self):
        """ Deserialize a Order """
        data = {"id":1, "name": "kitty", "time": "cat", "status": True}
        order = Order(data['id'])
        order.deserialize(data)
        self.assertNotEqual(order, None)
        self.assertEqual(order.id, 1)
        self.assertEqual(order.name, "kitty")
        self.assertEqual(order.time, "cat")

    def test_deserialize_with_no_name(self):
        """ Deserialize a Order that has no name """
        data = {"id":0, "time": "cat"}
        order = Order(0)
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Order that has no data """
        order = Order(0)
        self.assertRaises(DataValidationError, order.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserialize a Order that has bad data """
        order = Order(0)
        self.assertRaises(DataValidationError, order.deserialize, "string data")

    def test_save_a_order_with_no_name(self):
        """ Save a Order with no name """
        order = Order(0, None, "cat")
        self.assertRaises(DataValidationError, order.save)

    def test_find_order(self):
        """ Find a Order by id """
        Order(0, "fido", "dog").save()
        Order(0, "kitty", "cat").save()
        order = Order.find(2)
        self.assertIsNot(order, None)
        self.assertEqual(order.id, 2)
        self.assertEqual(order.name, "kitty")

    def test_find_with_no_orders(self):
        """ Find a Order with empty database """
        order = Order.find(1)
        self.assertIs(order, None)

    def test_order_not_found(self):
        """ Find a Order that doesnt exist """
        Order(0, "fido", "dog").save()
        order = Order.find(2)
        self.assertIs(order, None)

    def test_find_by_name(self):
        """ Find a Order by Name """
        Order(0, "fido", "dog").save()
        Order(0, "kitty", "cat").save()
        orders = Order.find_by_name("fido")
        self.assertNotEqual(len(orders), 0)
        self.assertEqual(orders[0].time, "dog")
        self.assertEqual(orders[0].name, "fido")

    def test_find_by_time(self):
        """ Find a Order by Time """
        Order(0, "fido", "dog").save()
        Order(0, "kitty", "cat").save()
        orders = Order.find_by_time("cat")
        self.assertNotEqual(len(orders), 0)
        self.assertEqual(orders[0].time, "cat")
        self.assertEqual(orders[0].name, "kitty")

    def test_find_by_availability(self):
        """ Find a Order by Availability """
        Order(0, "fido", "dog", False).save()
        Order(0, "kitty", "cat", True).save()
        orders = Order.find_by_availability(True)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].name, "kitty")

    def test_for_case_insensitive(self):
        """ Test for Case Insensitive Search """
        Order(0, "Fido", "DOG").save()
        Order(0, "Kitty", "CAT").save()
        orders = Order.find_by_name("fido")
        self.assertNotEqual(len(orders), 0)
        self.assertEqual(orders[0].name, "Fido")
        orders = Order.find_by_time("cat")
        self.assertNotEqual(len(orders), 0)
        self.assertEqual(orders[0].time, "CAT")

#    @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES).encode('utf8')})
    @patch.dict(os.environ, {'VCAP_SERVICES': VCAP_SERVICES})
    def test_vcap_services(self):
        """ Test if VCAP_SERVICES works """
        Order.init_db()
        self.assertIsNotNone(Order.redis)

    @patch('redis.Redis.ping')
    def test_redis_connection_error(self, ping_error_mock):
        """ Test a Bad Redis connection """
        ping_error_mock.side_effect = ConnectionError()
        self.assertRaises(ConnectionError, Order.init_db)
        self.assertIsNone(Order.redis)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestOrders)
    # unittest.TextTestRunner(verbosity=2).run(suite)
