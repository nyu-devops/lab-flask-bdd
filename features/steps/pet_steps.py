from os import getenv
import requests
from behave import *
import json
from app import server

BASE_URL = getenv('BASE_URL', 'http://localhost:5000/')

@when(u'I visit the "home page"')
def step_impl(context):
    # context.resp = context.app.get('/')
    context.resp = requests.get(BASE_URL)

@then(u'I should see "{message}"')
def step_impl(context, message):
    assert message in context.resp.text

@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.text

@given(u'the following pets')
def step_impl(context):
    server.data_reset()
    for row in context.table:
        server.data_load({"name": row['name'], "category": row['category'], "available": row['available'] in ['True', 'true', '1']})

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
