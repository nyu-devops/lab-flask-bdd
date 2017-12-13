######################################################################
# Copyright 2016, 2017 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Order Model that uses Redis

You must initlaize this class before use by calling inititlize().
This class looks for an environment variable called VCAP_SERVICES
to get it's database credentials from. If it cannot find one, it
tries to connect to Redis on the localhost. If that fails it looks
for a server name 'redis' to connect to.
"""

import os
import json
import logging
import pickle
from cerberus import Validator
from redis import Redis
from redis.exceptions import ConnectionError
from app.custom_exceptions import DataValidationError

######################################################################
# Order Model for database
#   This class must be initialized with use_db(redis) before using
#   where redis is a value connection to a Redis database
######################################################################
class Order(object):
    """ Order interface to database """

    logger = logging.getLogger(__name__)
    redis = None
    schema = {
        'id': {'type': 'integer'},
        'name': {'type': 'string', 'required': True},
        'time': {'type': 'string', 'required': True},
        'status': {'type': 'boolean', 'required': True}
        }
    __validator = Validator(schema)

    def __init__(self, id=0, name=None, time=None, status=True):
        """ Constructor """
        self.id = int(id)
        self.name = name
        self.time = time
        self.status = status

    def save(self):
        """ Saves a Order in the database """
        if self.name is None:   # name is the only required field
            raise DataValidationError('name attribute is not set')
        if self.id == 0:
            self.id = Order.__next_index()
        Order.redis.set(self.id, pickle.dumps(self.serialize()))

    def delete(self):
        """ Deletes a Order from the database """
        Order.redis.delete(self.id)

    def serialize(self):
        """ serializes a Order into a dictionary """
        return {
            "id": self.id,
            "name": self.name,
            "time": self.time,
            "status": self.status
        }

    def deserialize(self, data):
        """ deserializes a Order my marshalling the data """
        if isinstance(data, dict) and Order.__validator.validate(data):
            self.name = data['name']
            self.time = data['time']
            self.status = data['status']
        else:
            raise DataValidationError('Invalid order data: ' + str(Order.__validator.errors))
        return self


######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################

    @staticmethod
    def __next_index():
        """ Increments the index and returns it """
        return Order.redis.incr('index')

    # @staticmethod
    # def use_db(redis):
    #     Order.__redis = redis

    @staticmethod
    def remove_all():
        """ Removes all Orders from the database """
        Order.redis.flushall()

    @staticmethod
    def all():
        """ Query that returns all Orders """
        # results = [Order.from_dict(redis.hgetall(key)) for key in redis.keys() if key != 'index']
        results = []
        for key in Order.redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Order.redis.get(key))
                order = Order(data['id']).deserialize(data)
                results.append(order)
        return results

######################################################################
#  F I N D E R   M E T H O D S
######################################################################

    @staticmethod
    def find(order_id):
        """ Query that finds Orders by their id """
        if Order.redis.exists(order_id):
            data = pickle.loads(Order.redis.get(order_id))
            order = Order(data['id']).deserialize(data)
            return order
        return None

    @staticmethod
    def __find_by(attribute, value):
        """ Generic Query that finds a key with a specific value """
        # return [order for order in Order.__data if order.time == time]
        Order.logger.info('Processing %s query for %s', attribute, value)
        if isinstance(value, str):
            search_criteria = value.lower() # make case insensitive
        else:
            search_criteria = value
        results = []
        for key in Order.redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Order.redis.get(key))
                # perform case insensitive search on strings
                if isinstance(data[attribute], str):
                    test_value = data[attribute].lower()
                else:
                    test_value = data[attribute]
                if test_value == search_criteria:
                    results.append(Order(data['id']).deserialize(data))
        return results

    @staticmethod
    def find_by_name(name):
        """ Query that finds Orders by their name """
        return Order.__find_by('name', name)

    @staticmethod
    def find_by_time(time):
        """ Query that finds Orders by their time """
        return Order.__find_by('time', time)

    @staticmethod
    def find_by_availability(status=True):
        """ Query that finds Orders by their availability """
        return Order.__find_by('status', status)

######################################################################
#  R E D I S   D A T A B A S E   C O N N E C T I O N   M E T H O D S
######################################################################

    @staticmethod
    def connect_to_redis(hostname, port, password):
        """ Connects to Redis and tests the connection """
        Order.logger.info("Testing Connection to: %s:%s", hostname, port)
        Order.redis = Redis(host=hostname, port=port, password=password)
        try:
            Order.redis.ping()
            Order.logger.info("Connection established")
        except ConnectionError:
            Order.logger.info("Connection Error from: %s:%s", hostname, port)
            Order.redis = None
        return Order.redis

    @staticmethod
    def init_db(redis=None):
        """
        Initialized Redis database connection

        This method will work in the following conditions:
          1) In Bluemix with Redis bound through VCAP_SERVICES
          2) With Redis running on the local server as with Travis CI
          3) With Redis --link in a Docker container called 'redis'
          4) Passing in your own Redis connection object

        Exception:
        ----------
          redis.ConnectionError - if ping() test fails
        """
        if redis:
            Order.logger.info("Using client connection...")
            Order.redis = redis
            try:
                Order.redis.ping()
                Order.logger.info("Connection established")
            except ConnectionError:
                Order.logger.error("Client Connection Error!")
                Order.redis = None
                raise ConnectionError('Could not connect to the Redis Service')
            return
        # Get the credentials from the Bluemix environment
        if 'VCAP_SERVICES' in os.environ:
            Order.logger.info("Using VCAP_SERVICES...")
            vcap_services = os.environ['VCAP_SERVICES']
            services = json.loads(vcap_services)
            creds = services['rediscloud'][0]['credentials']
            Order.logger.info("Conecting to Redis on host %s port %s",
                            creds['hostname'], creds['port'])
            Order.connect_to_redis(creds['hostname'], creds['port'], creds['password'])
        else:
            Order.logger.info("VCAP_SERVICES not found, checking localhost for Redis")
            Order.connect_to_redis('127.0.0.1', 6379, None)
            if not Order.redis:
                Order.logger.info("No Redis on localhost, looking for redis host")
                Order.connect_to_redis('redis', 6379, None)
        if not Order.redis:
            # if you end up here, redis instance is down.
            Order.logger.fatal('*** FATAL ERROR: Could not connect to the Redis Service')
            raise ConnectionError('Could not connect to the Redis Service')
