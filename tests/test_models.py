# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
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
Test cases for Pet Model
"""
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from datetime import date
from wsgi import app
from service.models import db, Records, DataValidationError
from tests.factories import RecordFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:pgs3cr3t@localhost:5432/testdb"
)


class TestRecords(TestCase):

    # pylint: disable=duplicate-code
    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        # db.session.query(Records).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def test_create_record(self):
        """It should Create a record and assert that it exists"""
        record = RecordFactory()
        print(record)
        record.create()
        self.assertTrue(record.record_id is not None)

    def test_find_record(self):
        """It should Find a record by ID"""
        record = RecordFactory.create()
        db.session.add(record)
        db.session.commit()
        found = Records.query.get(record.record_id)
        self.assertEqual(found.serialize(), record.serialize())

    def test_update_record(self):
        """It should Update a record's details"""
        record = RecordFactory.create()
        db.session.add(record)
        db.session.commit()
        updates = {"first_name": "UpdatedName"}
        record.update(updates)
        self.assertEqual(record.first_name, "UpdatedName")

    def test_delete_record(self):
        """It should Delete a record"""
        record = RecordFactory.create()
        db.session.add(record)
        db.session.commit()
        record_id = record.record_id
        record.delete()
        self.assertIsNone(Records.query.get(record_id))
