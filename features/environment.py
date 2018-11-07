"""
Environment for Behave Testing
"""
import os
from behave import *
from selenium import webdriver

WAIT_SECONDS = 120
BASE_URL = os.getenv('BASE_URL', 'http://localhost:5000')

def before_all(context):
    """ Executed once before all tests """
    context.driver = webdriver.PhantomJS()
    # context.driver.manage().timeouts().pageLoadTimeout(WAIT_SECONDS, TimeUnit.SECONDS);
    # context.driver.manage().timeouts().setScriptTimeout(WAIT_SECONDS, TimeUnit.SECONDS);
    context.driver.implicitly_wait(WAIT_SECONDS) # seconds
    context.driver.set_window_size(1120, 550)
    context.base_url = BASE_URL
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini"
    context.config.setup_logging()

