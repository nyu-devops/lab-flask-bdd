"""
Pet Steps

Steps file for Pet.feature
"""
# Sample expect syntax
# expect(resp.status_code).to(equal(200))
# expect('Pet Demo REST API Service' in resp.data).to(be_true)
# expect(len(resp.data)).to(be_above(0))
# expect(data).to(have_key('name', match('kitty')))

from os import getenv
import json
import requests
from behave import *
from expects import *
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
    expect(message in context.driver.title).to(be_true)

@then(u'I should not see "{message}"')
def step_impl(context, message):
    expect(message in context.resp.text).to(be_false)

@when(u'I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = 'pet_' + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clean button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################

@when(u'I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower() + '-btn'
    context.driver.find_element_by_id(button_id).click()

@then(u'I should see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    expect(name in element.text).to(be_true)

@then(u'I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element_by_id('search_results')
    expect(name in element.text).to(be_false)

@then(u'I should see the message "{message}"')
def step_impl(context, message):
    element = context.driver.find_element_by_id('flash_message')
    expect(message in element.text).to(be_true)

##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by 'pet_' so the Name field has an id='pet_name'
# We can then lowercase the name and prefix with pet_ to get the id
##################################################################

@then(u'I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = 'pet_' + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    expect(text_string in element.get_attribute('value')).to(be_true)

@when(u'I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = 'pet_' + element_name.lower()
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

# @when(u'I change "{key}" to "{value}"')
# def step_impl(context, key, value):
#     context.data[key] = value

# @then(u'I should see "{message}" in "{field}"')
# def step_impl(context, message, field):
#     """ Check a field for text """
#     element = context.driver.find_element_by_id(field)
#     assert message in element.text
