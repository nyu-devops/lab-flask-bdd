# Test cases can be run with either of the following:
# python -m unittest discover
# nosetests -v --rednose --nologcapture

import unittest
import json
from redis import Redis
from werkzeug.exceptions import NotFound
from app.models import Pet
from app.custom_exceptions import DataValidationError
from app import server  # to get Redis

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPets(unittest.TestCase):

    def setUp(self):
        server.inititalize_redis()
        Pet.use_db(server.redis)
        # Pet.use_db(Redis(host='127.0.0.1', port=6379))
        Pet.remove_all()
        # Pet(0, 'fido', 'dog').save()
        # Pet(0, 'kitty', 'cat').save()

    def test_create_a_pet(self):
        # Create a pet and assert that it exists
        pet = Pet(0, "fido", "dog")
        self.assertNotEqual( pet, None )
        self.assertEqual( pet.id, 0 )
        self.assertEqual( pet.name, "fido" )
        self.assertEqual( pet.category, "dog" )

    def test_add_a_pet(self):
        # Create a pet and add it to the database
        pets = Pet.all()
        self.assertEqual( pets, [])
        pet = Pet(0, "fido", "dog")
        self.assertTrue( pet != None )
        self.assertEqual( pet.id, 0 )
        pet.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual( pet.id, 1 )
        pets = Pet.all()
        self.assertEqual( len(pets), 1)
        self.assertEqual( pets[0].id, 1 )
        self.assertEqual( pets[0].name, "fido" )
        self.assertEqual( pets[0].category, "dog" )

    def test_update_a_pet(self):
        pet = Pet(0, "fido", "dog")
        pet.save()
        self.assertEqual( pet.id, 1 )
        # Change it an save it
        pet.category = "k9"
        pet.save()
        self.assertEqual( pet.id, 1 )
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        pets = Pet.all()
        self.assertEqual( len(pets), 1)
        self.assertEqual( pets[0].category, "k9")
        self.assertEqual( pets[0].name, "fido" )

    def test_delete_a_pet(self):
        pet = Pet(0, "fido", "dog")
        pet.save()
        self.assertEqual( len(Pet.all()), 1)
        # delete the pet and make sure it isn't in the database
        pet.delete()
        self.assertEqual( len(Pet.all()), 0)

    def test_serialize_a_pet(self):
        pet = Pet(0, "fido", "dog")
        data = pet.serialize()
        self.assertNotEqual( data, None )
        self.assertIn( 'id', data )
        self.assertEqual( data['id'], 0 )
        self.assertIn( 'name', data )
        self.assertEqual( data['name'], "fido" )
        self.assertIn( 'category', data )
        self.assertEqual( data['category'], "dog" )

    def test_deserialize_a_pet(self):
        data = {"id":1, "name": "kitty", "category": "cat"}
        pet = Pet(data['id'])
        pet.deserialize(data)
        self.assertNotEqual( pet, None )
        self.assertEqual( pet.id, 1 )
        self.assertEqual( pet.name, "kitty" )
        self.assertEqual( pet.category, "cat" )

    def test_deserialize_a_pet_with_no_name(self):
        data = {"id":0, "category": "cat"}
        pet = Pet(0)
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_a_pet_with_no_data(self):
        pet = Pet(0)
        self.assertRaises(DataValidationError, pet.deserialize, None)

    def test_deserialize_a_pet_with_bad_data(self):
        pet = Pet(0)
        self.assertRaises(DataValidationError, pet.deserialize, "string data")

    def test_find_pet(self):
        Pet(0, "fido", "dog").save()
        Pet(0, "kitty", "cat").save()
        pet = Pet.find(2)
        self.assertIsNot( pet, None)
        self.assertEqual( pet.id, 2 )
        self.assertEqual( pet.name, "kitty" )

    def test_find_with_no_pets(self):
        pet = Pet.find(1)
        self.assertIs( pet, None)

    def test_find_or_404(self):
        self.assertRaises(NotFound, Pet.find_or_404, 1)

    def test_pet_not_found(self):
        Pet(0, "fido", "dog").save()
        pet = Pet.find(2)
        self.assertIs( pet, None)

    def test_find_by_category(self):
        Pet(0, "fido", "dog").save()
        Pet(0, "kitty", "cat").save()
        pets = Pet.find_by_category("cat")
        self.assertNotEqual( len(pets), 0 )
        self.assertEqual( pets[0].category, "cat" )
        self.assertEqual( pets[0].name, "kitty" )


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestPets)
    # unittest.TextTestRunner(verbosity=2).run(suite)
