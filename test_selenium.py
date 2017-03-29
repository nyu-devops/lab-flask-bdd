
import unittest
from selenium import webdriver

class TestPetServerWeb(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)
        self.baseURL = "http://localhost:5000/"

    def tearDown(self):
        self.driver.quit()

    def test_index(self):
        self.driver.get(self.baseURL)
        self.assertEqual(self.driver.title, "Pet Demo RESTful Service")
        element = self.driver.find_element_by_id('message')
        self.assertEqual(element.text , "Pet Demo REST API Service")

    def test_get_pets(self):
        self.driver.get(self.baseURL)
        self.driver.find_element_by_id("get_pets").click()
        self.assertIn(
            "http://localhost:5000/pets", self.driver.current_url
        )
        print self.driver.current_url

        #
        # self.driver.find_element_by_id(
        #     'search_form_input_homepage').send_keys("realpython")
        # self.driver.find_element_by_id("search_button_homepage").click()
        # self.assertIn(
        #     "https://duckduckgo.com/?q=realpython", self.driver.current_url
        # )


if __name__ == '__main__':
    unittest.main()
