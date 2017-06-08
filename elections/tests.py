from django.test import TestCase
from elections.forms import CircuitForm
from elections.models import Circuit, Borough, Candidate, CandidateResult
from django.test import Client

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

from time import sleep


class BoroughSearchTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_no_search(self):
        context = self.client.get('/borough/search').context
        self.assertFalse(context["searched"])
        self.assertNotIn("results", context)

    def test_search_1(self):
        Borough.objects.create(name="asdkuhfaksfasf", code=1)
        response = self.client.get('/borough/search', {'query': "hfaks"})
        # check if searching was executed
        self.assertTrue(response.context["searched"])
        # check if found borough from database
        self.assertEqual(len(response.context["results"]), 1)
        # check HTML code - results should be printed out somewhere
        if len(response.context["results"]):
            self.assertContains(response, "asdkuhfaksfasf")

    def test_search_many(self):
        Borough.objects.create(name="a", code=1)
        Borough.objects.create(name="aa", code=2)
        Borough.objects.create(name="aaa", code=3)
        Borough.objects.create(name="b", code=4)
        response = self.client.get('/borough/search', {'query': "a"})
        self.assertEqual(len(response.context["results"]), 3)


class CircuitFormTest(TestCase):
    def setUp(self):
        self.circuit = Circuit.objects.create(
            address="Planet: Poland",
            cards=1000,
            valid_cards=500,
            borough=Borough.objects.create(name='b', code=1)
        )

        self.candidates = []
        self.candidates.append(Candidate.objects.create(first_name='A', last_name='B'))
        self.candidates.append(Candidate.objects.create(first_name='C', last_name='D'))

        for candidate in self.candidates:
            CandidateResult.objects.create(
                candidate=candidate,
                circuit=self.circuit,
                votes=0
            )

    def test_valid(self):
        data = {
            str(self.candidates[0].id): 1,
            str(self.candidates[1].id): 1,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertTrue(form.is_valid())

    def test_valid_2(self):
        data = {
            str(self.candidates[0].id): 50,
            str(self.candidates[1].id): 90,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertTrue(form.is_valid())

    def test_valid_3(self):
        data = {
            str(self.candidates[0].id): 0,
            str(self.candidates[1].id): 0,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertTrue(form.is_valid())

    def test_valid_4(self):
        data = {
            str(self.candidates[0].id): 500,
            str(self.candidates[1].id): 0,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertTrue(form.is_valid())

    def test_too_much_votes(self):
        data = {
            str(self.candidates[0].id): 1000,
            str(self.candidates[1].id): 2000,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertFalse(form.is_valid())

    def test_too_much_votes_2(self):
        data = {
            str(self.candidates[0].id): 0,
            str(self.candidates[1].id): 10000,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertFalse(form.is_valid())

    def test_negative_votes(self):
        data = {
            str(self.candidates[0].id): 100,
            str(self.candidates[1].id): -1,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertFalse(form.is_valid())

    def test_negative_votes_2(self):
        data = {
            str(self.candidates[0].id): -2,
            str(self.candidates[1].id): -2,
        }
        form = CircuitForm(data, circuit=self.circuit)
        self.assertFalse(form.is_valid())



class ElectionsTests(StaticLiveServerTestCase):
    url = "http://localhost:3000"

    @classmethod
    def setUpClass(cls):
        super(ElectionsTests, cls).setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

    def wait(self, driver, element):
        driver.set_script_timeout(10)
        driver.execute_async_script("""
                callback = arguments[arguments.length - 1];
                angular.element('""" + element + """').injector().get('$browser').notifyWhenNoOutstandingRequests(callback);""")

    @staticmethod
    def load_page(driver, url, expected_id, delay=3):
        driver.get(url)
        try:
            WebDriverWait(driver, delay).until(expected_conditions.presence_of_element_located((By.ID, expected_id)))
        except TimeoutException:
            assert False

    @staticmethod
    def login(driver, username_value, password_value):
        username_field = driver.find_element_by_id("username")
        username_field.clear()
        username_field.send_keys(username_value)

        password_field = driver.find_element_by_id("password")
        password_field.clear()
        password_field.send_keys(password_value)

        submit_button = driver.find_element_by_xpath('//*[@id="wrapper"]/ng-component/div/form/div[3]/button')
        submit_button.click()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('myuser')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('secret')
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()

    def test_login_valid(self):
        driver = self.selenium
        self.load_page(driver, self.url + "/login", 'username')
        self.login(driver, "mateusz", "mateuszmateusz")
        sleep(1)
        assert "Niepoprawne dane" not in driver.page_source

    def test_login_invalid(self):
        driver = self.selenium
        self.load_page(driver, self.url + "/login", 'username')
        self.login(driver, "jankowalski", "234567")
        sleep(1)
        assert "Niepoprawne dane" in driver.page_source

    def test_not_logged_in(self):
        driver = self.selenium
        driver.implicitly_wait(10)
        driver.get("http://localhost:3000/borough/293")
        driver.find_element_by_id("circuits")
        sleep(3000)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(ElectionsTests, cls).tearDownClass()
