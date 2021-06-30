"""
Pet Steps

Steps file for Pet.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import json
import requests
from behave import given
from compare import expect

@given('the following pets')
def step_impl(context):
    """ Delete all Pets and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the pets and delete them one by one
    context.resp = requests.get(context.base_url + '/pets', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for pet in context.resp.json():
        context.resp = requests.delete(context.base_url + '/pets/' + str(pet["_id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)
    
    # load the database with new pets
    create_url = context.base_url + '/pets'
    for row in context.table:
        data = {
            "name": row['name'],
            "category": row['category'],
            "available": row['available'] in ['True', 'true', '1']
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
