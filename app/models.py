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

import pickle
from cerberus import Validator
from flask import url_for
from werkzeug.exceptions import NotFound
from custom_exceptions import DataValidationError

######################################################################
# Pet Model for database
#   This class must be initialized with use_db(redis) before using
#   where redis is a value connection to a Redis database
######################################################################
class Pet(object):
    schema = {
                'id': {'type': 'integer'},
                'name': {'type': 'string', 'required': True},
                'category': {'type': 'string', 'required': True},
                'available': {'type': 'boolean', 'required': True}
             }
    __validator = Validator(schema)
    __redis = None

    def __init__(self, id=0, name=None, category=None, available=True):
        self.id = int(id)
        self.name = name
        self.category = category
        self.available = available

    def self_url(self):
        return url_for('get_pets', id=self.id, _external=True)

    def save(self):
        if self.name == None:   # name is the only required field
            raise AttributeError('name attribute is not set')
        if self.id == 0:
            self.id = self.__next_index()
        Pet.__redis.set(self.id, pickle.dumps(self.serialize()))

    def delete(self):
        Pet.__redis.delete(self.id)

    def __next_index(self):
        return Pet.__redis.incr('index')

    def serialize(self):
        return { "id": self.id, "name": self.name, "category": self.category, "available": self.available }

    def deserialize(self, data):
        if isinstance(data, dict) and Pet.__validator.validate(data):
            self.name = data['name']
            self.category = data['category']
            self.available = data['available']
        else:
            raise DataValidationError('Invalid pet data: ' + str(Pet.__validator.errors))
        return self

######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################

    @staticmethod
    def use_db(redis):
        Pet.__redis = redis

    @staticmethod
    def remove_all():
        Pet.__redis.flushall()

    @staticmethod
    def all():
        # results = [Pet.from_dict(redis.hgetall(key)) for key in redis.keys() if key != 'index']
        results = []
        for key in Pet.__redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Pet.__redis.get(key))
                pet = Pet(data['id']).deserialize(data)
                results.append(pet)
        return results

    @staticmethod
    def find(id):
        if Pet.__redis.exists(id):
            data = pickle.loads(Pet.__redis.get(id))
            pet = Pet(data['id']).deserialize(data)
            return pet
        else:
            return None

    @staticmethod
    def find_or_404(id):
        pet = Pet.find(id)
        if not pet:
            raise NotFound("Pet with id '{}' was not found.".format(id))
        return pet

    @staticmethod
    def find_by_category(category):
        # return [pet for pet in Pet.__data if pet.category == category]
        results = []
        for key in Pet.__redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Pet.__redis.get(key))
                if data['category'] == category:
                    results.append(Pet(data['id']).deserialize(data))
        return results

    @staticmethod
    def find_by_availability(available=True):
        # return [pet for pet in Pet.__data if pet.available == available]
        results = []
        for key in Pet.__redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Pet.__redis.get(key))
                if data['available'] == available:
                    results.append(Pet(data['id']).deserialize(data))
        return results
