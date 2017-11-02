"""
Pet Steps

Steps file for Pet.feature
"""

from os import getenv
import json
import requests
from behave import *
from app import server

BASE_URL = getenv('BASE_URL', 'http://localhost:5000/')

@given(u'the following pets')
def step_impl(context):
    """ Delete all Pets and load new ones """
    headers = {'Content-Type': 'application/json'}
    context.resp = requests.delete(context.base_url + '/pets/reset', headers=headers)
    assert context.resp.status_code == 204
    create_url = context.base_url + '/pets'
    for row in context.table:
        data = {
            "name": row['name'],
            "category": row['category'],
            "available": row['available'] in ['True', 'true', '1']
            }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        assert context.resp.status_code == 201

@when(u'I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)

@then(u'I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    assert message in context.driver.title

@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.text

@when(u'I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = 'pet_' + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

@when(u'I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then(u'I should see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    assert name in element.text

@then(u'I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    assert name not in element.text

@then(u'I should see the message "{message}"')
def step_impl(context, message):
    element = context.driver.find_element_by_id('flash_message')
    assert message in element.text

@then(u'I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = 'pet_' + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    assert text_string in element.get_attribute('value')

@when(u'I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = 'pet_' + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)


# @then(u'I should see "{message}" in "{field}"')
# def step_impl(context, message, field):
#     """ Check a field for text """
#     element = context.driver.find_element_by_id(field)
#     assert message in element.text

# @when(u'I change "{key}" to "{value}"')
# def step_impl(context, key, value):
#     context.data[key] = value
