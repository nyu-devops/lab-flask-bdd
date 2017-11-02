from os import getenv
import requests
from behave import *
import json
from app import server

BASE_URL = getenv('BASE_URL', 'http://localhost:5000/')

@when(u'I visit the "home page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)

@then(u'I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    assert message in context.driver.title

@then(u'I should see "{message}" in "{field}"')
def step_impl(context, message, field):
    """ Check a field for text """
    element = context.driver.find_element_by_id(field)
    assert message in element.text

@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.text

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

@when(u'I set the "{element_id}" to "{text_string}"')
def step_impl(context, element_id, text_string):
    element = context.driver.find_element_by_id(element_id)
    element.clear()
    element.send_keys(text_string)

@when(u'I press the "{submit}" button')
def step_impl(context, submit):
    context.driver.find_element_by_id(submit).click()

@then(u'I should see the message "{message}"')
def step_impl(context, message):
    element = context.driver.find_element_by_id('flash_message')
    assert message in element.text

        # self.driver.get(self.baseURL)
        # nameElement = self.driver.find_element_by_name("name")
        # nameElement.clear()
        # nameElement.send_keys("Missy")
        # categoryElement = self.driver.find_element_by_name("category")
        # categoryElement.clear()
        # categoryElement.send_keys("Cat")
        # self.driver.find_element_by_id("submit").click()
        # # make sure we landed on the correct page
        # new_url = '{}pets'.format(self.baseURL)
        # self.assertIn(new_url, self.driver.current_url)
        # print self.driver.current_url




@when(u'I visit "{url}"')
def step_impl(context, url):
    # context.resp = context.app.get(url)
    context.resp = requests.get(BASE_URL + url)
    assert context.resp.status_code == 200

@when(u'I delete "{url}" with id "{id}"')
def step_impl(context, url, id):
    target_url = '{}/{}'.format(url, id)
    # context.resp = context.app.delete(target_url)
    context.resp = requests.delete(BASE_URL + target_url)
    assert context.resp.status_code == 204
    assert context.resp.text is u''

@when(u'I retrieve "{url}" with id "{id}"')
def step_impl(context, url, id):
    target_url = '{}/{}'.format(url, id)
    # context.resp = context.app.get(target_url)
    context.resp = requests.get(BASE_URL + target_url)
    context.data = context.resp.json()
    assert context.resp.status_code == 200

@when(u'I change "{key}" to "{value}"')
def step_impl(context, key, value):
    context.data[key] = value

@when(u'I update "{url}" with id "{id}"')
def step_impl(context, url, id):
    target_url = '{}/{}'.format(url, id)
    headers = {'content-type': 'application/json'}
    data = json.dumps(context.data)
    context.resp = requests.put(BASE_URL + target_url, data=data, headers=headers)
    assert context.resp.status_code == 200

# @then(u'I should see a list of pets')
# def step_impl(context):
#     assert context.resp.status_code == 200
#     assert len(context.resp.data) > 0
