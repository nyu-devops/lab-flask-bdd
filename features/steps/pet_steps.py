from behave import *
import json
from app import server

@when(u'I visit the "home page"')
def step_impl(context):
    context.resp = context.app.get('/')

@then(u'I should see "{message}"')
def step_impl(context, message):
    assert message in context.resp.data

@then(u'I should not see "{message}"')
def step_impl(context, message):
    assert message not in context.resp.data

@given(u'the following pets')
def step_impl(context):
    server.data_reset()
    for row in context.table:
        server.data_load({"name": row['name'], "category": row['category']})

@when(u'I visit "{url}"')
def step_impl(context, url):
    context.resp = context.app.get(url)
    assert context.resp.status_code == 200

@when(u'I delete "{url}"')
def step_impl(context, url):
    context.resp = context.app.delete(url)
    assert context.resp.status_code == 204
    assert context.resp.data is ""

@when(u'I retrieve "{url}"')
def step_impl(context, url):
    context.resp = context.app.get(url)
    assert context.resp.status_code == 200

@when(u'I change "{key}" to "{value}"')
def step_impl(context, key, value):
    data = json.loads(context.resp.data)
    data[key] = value
    context.resp.data = json.dumps(data)

@when(u'I update "{url}"')
def step_impl(context, url):
    context.resp = context.app.put(url, data=context.resp.data, content_type='application/json')
    assert context.resp.status_code == 200

# @then(u'I should see a list of pets')
# def step_impl(context):
#     assert context.resp.status_code == 200
#     assert len(context.resp.data) > 0
