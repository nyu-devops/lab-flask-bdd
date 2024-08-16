# Copyright 2016, 2024 John Rofrano. All Rights Reserved.
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

"""
Models for Records Demo Service

All of the models are stored in this module

Models
------
Records

Attributes:
-----------
record_id
first_name
last_name
age
sex
bmi
children
smoke
region

"""
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Records(db.Model):
    """
    Class that represents a Record in the dataset.
    """

    ##################################################
    # Table Schema
    ##################################################
    record_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)  # 'Male' or 'Female'
    bmi = db.Column(db.Float, nullable=False)
    children = db.Column(db.Integer, nullable=False)
    smoke = db.Column(db.Boolean, nullable=False)
    region = db.Column(db.String(100), nullable=False)

    ##################################################
    # Methods
    ##################################################

    def serialize(self):
        """Returns the object data in easily serializable format"""
        return {
            "Record ID": self.record_id,
            "First Name": self.first_name,
            "Last Name": self.last_name,
            "Age": self.age,
            "Sex": self.sex,
            "BMI": self.bmi,
            "Children": self.children,
            "Smoke": self.smoke,
            "Region": self.region,
        }

    @classmethod
    def deserialize(cls, data):
        """Deserializes Records from a dictionary."""
        try:
            return cls(
                first_name=data.get("First Name"),
                last_name=data.get("Last Name"),
                age=data["Age"],
                sex=data["Sex"],
                bmi=data["BMI"],
                children=data["Children"],
                smoke=data["Smoke"],
                region=data["Region"],
            )
        except KeyError as e:
            raise DataValidationError('Invalid record: missing ' + e.args[0]) from e

    def create(self):
        """Adds a new Record to the database."""
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """Updates a Record with data from a dictionary."""
        for key, value in data.items():
            setattr(self, key.lower().replace(" ", "_"), value)
        db.session.commit()

    def delete(self):
        """Deletes a Record from the database."""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_all(cls):
        """Returns all Records."""
        return cls.query.all()
