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
    # context.driver = webdriver.PhantomJS()
    # context.driver.manage().timeouts().pageLoadTimeout(WAIT_SECONDS, TimeUnit.SECONDS);
    # context.driver.manage().timeouts().setScriptTimeout(WAIT_SECONDS, TimeUnit.SECONDS);
    # context.driver.implicitly_wait(WAIT_SECONDS) # seconds
    # context.driver.set_window_size(1120, 550)

    options = webdriver.ChromeOptions()
    # options.add_argument('window-size=1200x600')
    options.add_argument("start-maximized") # open Browser in maximized mode
    options.add_argument("disable-infobars") # disabling infobars
    options.add_argument("--disable-extensions") # disabling extensions
    options.add_argument("--disable-gpu") # applicable to windows os only
    options.add_argument("--disable-dev-shm-usage") # overcome limited resource problems
    options.add_argument("--no-sandbox") # Bypass OS security model
    options.add_argument("--headless")
    context.driver = webdriver.Chrome(options=options)
    context.driver.implicitly_wait(WAIT_SECONDS) # seconds
    # context.driver.set_window_size(1200, 600)

    context.base_url = BASE_URL
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini"
    context.config.setup_logging()


def after_all(context):
    """ Executed after all tests """
    context.driver.quit()
