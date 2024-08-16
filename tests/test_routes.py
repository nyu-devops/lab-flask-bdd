# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
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
"""

import os
import logging
import json
from unittest import TestCase
from unittest.mock import patch, MagicMock

# from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus
from wsgi import app

# from service import create_app
from service.common import status
from service.models import Records, db, DataValidationError
from tests.factories import RecordFactory

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
# logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:pgs3cr3t@localhost:5432/testdb"
)
BASE_URL = "/pets"

# app = create_app()


######################################################################
#  T E S T   P E T   S E R V I C E
######################################################################
class TestPetService(TestCase):
    """Pet Server Tests"""

    # pylint: disable=duplicate-code
    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Records).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Pet Demo REST API Service", response.data)

    def test_health(self):
        """It should be healthy"""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------

    def test_create_record(self):
        """It should create a record via POST."""
        record = RecordFactory.build()
        response = self.client.post(
            "/records",
            data=json.dumps(record.serialize()),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        print(data)
        self.assertEqual(data["First Name"], record.first_name)

    def test_get_record(self):
        """It should get a record via GET."""
        record = RecordFactory.create()
        db.session.add(record)
        db.session.commit()
        response = self.client.get(f"/records/{record.record_id}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["First Name"], record.first_name)

    def test_update_record(self):
        """It should update a record via PUT."""
        record = RecordFactory.create()
        db.session.add(record)
        db.session.commit()
        updates = {"first_name": "Updated"}
        response = self.client.put(
            f"/records/{record.record_id}",
            data=json.dumps(updates),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["First Name"], "Updated")

    def test_delete_record(self):
        """It should delete a record via DELETE."""
        record = RecordFactory.create()
        db.session.add(record)
        db.session.commit()
        response = self.client.delete(f"/records/{record.record_id}")
        self.assertEqual(response.status_code, 204)
        response = self.client.get(f"/records/{record.record_id}")
        self.assertEqual(response.status_code, 404)
