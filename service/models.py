######################################################################
# Copyright 2016, 2022 John Rofrano. All Rights Reserved.
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
Pet Model that uses Cloudant

You must initialize this class before use by calling initialize().
This class looks for an environment variable called VCAP_SERVICES
to get it's database credentials from. If it cannot find one, it
tries to connect to Cloudant on the localhost. If that fails it looks
for a server name 'cloudant' to connect to.

To use with Docker couchdb database use:
    docker run -d --name couchdb -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=pass couchdb

Docker Note:
    CouchDB uses /opt/couchdb/data to store its data, and is exposed as a volume
    e.g., to use current folder add: -v $(pwd):/opt/couchdb/data
    You can also use Docker volumes like this: -v couchdb_data:/opt/couchdb/data
"""

import os
import json
import logging
from enum import Enum
from signal import raise_signal
from retry import retry
from datetime import date
from cloudant.client import Cloudant
from cloudant.query import Query
from cloudant.adapters import Replay429Adapter
from cloudant.database import CloudantDatabase
from requests import HTTPError, ConnectionError

# get configuration from environment (12-factor)
ADMIN_PARTY = os.environ.get("ADMIN_PARTY", "False").lower() == "true"
CLOUDANT_HOST = os.environ.get("CLOUDANT_HOST", "localhost")
CLOUDANT_USERNAME = os.environ.get("CLOUDANT_USERNAME", "admin")
CLOUDANT_PASSWORD = os.environ.get("CLOUDANT_PASSWORD", "pass")

# global variables for retry (must be int)
RETRY_COUNT = int(os.environ.get("RETRY_COUNT", 10))
RETRY_DELAY = int(os.environ.get("RETRY_DELAY", 1))
RETRY_BACKOFF = int(os.environ.get("RETRY_BACKOFF", 2))


class DatabaseConnectionError(Exception):
    """Custom Exception when database connection fails"""


class DataValidationError(Exception):
    """Custom Exception with data validation fails"""


class Gender(Enum):
    """Enumeration of valid Pet Genders"""

    MALE = 0
    FEMALE = 1
    UNKNOWN = 3


class Pet:
    """
    Class that represents a Pet

    This version uses a NoSQL database for persistence
    """

    logger = logging.getLogger(__name__)
    client: Cloudant = None
    database: CloudantDatabase = None

    def __init__(
        self,
        name: str = None,
        category: str = None,
        available: bool = True,
        gender: Gender = Gender.UNKNOWN,
        birthday: date = date.today(),
    ):
        """Constructor"""
        self.id = None  # pylint: disable=invalid-name
        self.name = name
        self.category = category
        self.available = available
        self.gender = gender
        self.birthday = birthday

    def __repr__(self):
        return f"<Pet {self.name} id=[{self.id}]>"

    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
    def create(self):
        """
        Creates a new Pet in the database
        """
        if self.name is None:  # name is the only required field
            raise DataValidationError("name attribute is not set")

        try:
            document = self.database.create_document(self.serialize())
        except HTTPError as err:
            Pet.logger.warning("Create failed: %s", err)
            return

        if document.exists():
            self.id = document["_id"]

    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
    def update(self):
        """Updates a Pet in the database"""
        try:
            document = self.database[self.id]
        except KeyError:
            document = None
        if document:
            document.update(self.serialize())
            document.save()

    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
    def delete(self):
        """Deletes a Pet from the database"""
        try:
            document = self.database[self.id]
        except KeyError:
            document = None
        if document:
            document.delete()

    def serialize(self) -> dict:
        """serializes a Pet into a dictionary"""
        pet = {
            "name": self.name,
            "category": self.category,
            "available": self.available,
            "gender": self.gender.name,  # convert enum to string
            "birthday": self.birthday.isoformat()
        }
        if self.id:
            pet["_id"] = self.id
        return pet

    def deserialize(self, data: dict) -> None:
        """deserializes a Pet my marshalling the data.

        :param data: a Python dictionary representing a Pet.
        """
        Pet.logger.info("deserialize(%s)", data)
        try:
            self.name = data["name"]
            self.category = data["category"]
            if isinstance(data["available"], bool):
                self.available = data["available"]
            else:
                raise DataValidationError("Invalid type for boolean [available]: " + str(type(data["available"])))
            self.gender = getattr(Gender, data["gender"])  # create enum from string
            self.birthday = date.fromisoformat(data["birthday"])
        except KeyError as error:
            raise DataValidationError("Invalid pet: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError("Invalid pet: body of request contained bad or no data")

        # if there is no id and the data has one, assign it
        if not self.id and "_id" in data:
            self.id = data["_id"]

        return self

    ######################################################################
    #  S T A T I C   D A T A B S E   M E T H O D S
    ######################################################################

    @classmethod
    def connect(cls):
        """Connect to the server"""
        cls.client.connect()

    @classmethod
    def disconnect(cls):
        """Disconnect from the server"""
        cls.client.disconnect()

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
    def create_query_index(cls, field_name: str, order: str = "asc"):
        """Creates a new query index for searching"""
        cls.database.create_query_index(index_name=field_name, fields=[{field_name: order}])

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
    def remove_all(cls):
        """Removes all documents from the database (use for testing)"""
        for document in cls.database:
            document.delete()

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
    def all(cls):
        """Query that returns all Pets"""
        results = []
        for doc in cls.database:
            pet = Pet().deserialize(doc)
            pet.id = doc["_id"]
            results.append(pet)
        return results

    ######################################################################
    #  F I N D E R   M E T H O D S
    ######################################################################

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
    def find_by(cls, **kwargs):
        """Find records using selector"""
        query = Query(cls.database, selector=kwargs)
        results = []
        for doc in query.result:
            pet = Pet()
            pet.deserialize(doc)
            results.append(pet)
        return results

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
    def find(cls, pet_id: str):
        """Query that finds Pets by their id"""
        try:
            document = cls.database[pet_id]
            # Cloudant doesn't delete documents. :( It leaves the _id with no data
            # so we must validate that _id that came back has a valid _rev
            # if this next line throws a KeyError the document was deleted
            _ = document['_rev']
            return Pet().deserialize(document)
        except KeyError:
            return None

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
    def find_by_name(cls, name: str):
        """Query that finds Pets by their name"""
        return cls.find_by(name=name)

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
    def find_by_category(cls, category: str):
        """Query that finds Pets by their category"""
        return cls.find_by(category=category)

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
    def find_by_availability(cls, available: bool = True):
        """Query that finds Pets by their availability"""
        return cls.find_by(available=available)

    @classmethod
    @retry(HTTPError, delay=RETRY_DELAY, backoff=RETRY_BACKOFF, tries=RETRY_COUNT, logger=logger)
    def find_by_gender(cls, gender: str = Gender.UNKNOWN.name):
        """Query that finds Pets by their gender as a string"""
        return cls.find_by(gender=gender)

    ############################################################
    #  C L O U D A N T   D A T A B A S E   C O N N E C T I O N
    ############################################################

    @staticmethod
    def init_db(dbname: str = "pets"):
        """
        Initialized Cloudant database connection
        """
        opts = {}
        # Try and get VCAP from the environment
        if "VCAP_SERVICES" in os.environ:
            Pet.logger.info("Found Cloud Foundry VCAP_SERVICES bindings")
            vcap_services = json.loads(os.environ["VCAP_SERVICES"])
            # Look for Cloudant in VCAP_SERVICES
            for service in vcap_services:
                if service.startswith("cloudantNoSQLDB"):
                    opts = vcap_services[service][0]["credentials"]

        # if VCAP_SERVICES isn't found, maybe we are running on Kubernetes?
        if not opts and "BINDING_CLOUDANT" in os.environ:
            Pet.logger.info("Found Kubernetes BINDING_CLOUDANT bindings")
            opts = json.loads(os.environ["BINDING_CLOUDANT"])

        # If Cloudant not found in VCAP_SERVICES or BINDING_CLOUDANT
        # get it from the CLOUDANT_xxx environment variables
        if not opts:
            Pet.logger.info("VCAP_SERVICES and BINDING_CLOUDANT undefined.")
            opts = {
                "username": CLOUDANT_USERNAME,
                "password": CLOUDANT_PASSWORD,
                "host": CLOUDANT_HOST,
                "port": 5984,
                "url": "http://" + CLOUDANT_HOST + ":5984/",
            }

        if any(k not in opts for k in ("host", "username", "password", "port", "url")):
            raise DatabaseConnectionError(
                "Error - Failed to retrieve options. " "Check that app is bound to a Cloudant service."
            )

        Pet.logger.info("Cloudant Endpoint: %s", opts["url"])
        try:
            if ADMIN_PARTY:
                Pet.logger.info("Running in Admin Party Mode...")
            Pet.client = Cloudant(
                opts["username"],
                opts["password"],
                url=opts["url"],
                connect=True,
                auto_renew=True,
                admin_party=ADMIN_PARTY,
                adapter=Replay429Adapter(retries=10, initialBackoff=0.01),
            )

        except ConnectionError:
            raise DatabaseConnectionError("Cloudant service could not be reached")

        # Create database if it doesn't exist
        try:
            Pet.database = Pet.client[dbname]
        except KeyError:
            # Create a database using an initialized client
            Pet.database = Pet.client.create_database(dbname)
        # check for success
        if not Pet.database.exists():
            raise DatabaseConnectionError("Database [{}] could not be obtained".format(dbname))
