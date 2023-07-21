"""
Environment for Behave Testing
"""
from os import getenv
from selenium import webdriver

WAIT_SECONDS = int(getenv('WAIT_SECONDS', '60'))
BASE_URL = getenv('BASE_URL', 'http://localhost:8080')


def before_all(context):
    """ Executed once before all tests """
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS
    # Setup Chrome webdriver
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--headless")
    context.driver = webdriver.Chrome(options=options)
    context.driver.implicitly_wait(context.wait_seconds)  # seconds
    # -- SET LOG LEVEL: behave --logging-level=ERROR ...
    # on behave command-line or in "behave.ini"
    context.config.setup_logging()


def after_all(context):
    """ Executed after all tests """
    context.driver.quit()
