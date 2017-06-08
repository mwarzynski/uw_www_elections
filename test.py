import unittest

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By


class Elections(unittest.TestCase):

    url = "http://localhost:3000"

    def setUp(self):
        self.driver = webdriver.Chrome()

    @staticmethod
    def wait_for(driver, by, what, delay=3):
        try:
            WebDriverWait(driver, delay).until(expected_conditions.presence_of_element_located((by, what)))
        except TimeoutException:
            assert False

    def login(self, driver, username_value, password_value):
        driver.get(self.url + '/login')
        self.wait_for(driver, By.ID, 'username')
        username_field = driver.find_element_by_id("username")
        username_field.clear()
        username_field.send_keys(username_value)

        password_field = driver.find_element_by_id("password")
        password_field.clear()
        password_field.send_keys(password_value)

        submit_button = driver.find_element_by_xpath('//*[@id="wrapper"]/ng-component/div/form/div[3]/button')
        submit_button.click()

    def test_login_valid(self):
        driver = self.driver
        self.login(driver, "mateusz", "mateuszmateusz")
        self.wait_for(driver, By.ID, 'map') # map is only on / when we should be redirected

    def test_login_invalid(self):
        driver = self.driver
        self.login(driver, "jankowalski", "234567")
        self.wait_for(driver, By.XPATH, '//*[@id="wrapper"]/ng-component/div/form/div[1]')
        assert "Niepoprawne dane" in driver.page_source

    def test_go_through_displays(self):
        driver = self.driver
        self.login(driver, "mateusz", "mateuszmateusz")
        self.wait_for(driver, By.ID, 'map')

        driver.get(self.url + '/voivodeship/2')
        self.wait_for(driver, By.CSS_SELECTOR, '#wrapper > ng-component > pages > section > ul > li:nth-child(1) > a', delay=1000)
        link = driver.find_element_by_css_selector('#wrapper > ng-component > pages > section > ul > li:nth-child(1) > a')
        link.click()

        self.wait_for(driver, By.CSS_SELECTOR, '#wrapper > ng-component > pages > section > ul > li:nth-child(1) > a')
        link = driver.find_element_by_css_selector('#wrapper > ng-component > pages > section > ul > li:nth-child(1) > a')
        link.click()

        try:
            driver.find_element_by_css_selector('#circuits > table > tbody > tr:nth-child(1) > td:nth-child(2) > a')
            assert False
        except NoSuchElementException:
            assert True

    def test_search_valid(self):
        driver = self.driver
        driver.get(self.url + '/borough/search')
        self.wait_for(driver, By.ID, 'search')

        password_field = driver.find_element_by_id("search")
        password_field.clear()
        password_field.send_keys("Iwaniska")

        driver.find_element_by_css_selector('#wrapper > borough-search > section > form > div:nth-child(2) > button').click()
        self.wait_for(driver, By.CSS_SELECTOR, '#wrapper > borough-search > section.results > ul > li > a')

        for li in driver.find_elements(By.XPATH, '//*[@id="wrapper"]/borough-search/section[2]/ul/li'):
            assert 'iwaniska' in li.text.lower()

        driver.find_element_by_xpath('//*[@id="wrapper"]/borough-search/section[2]/ul/li').click()
        self.wait_for(driver, By.XPATH, '//*[@id="top_header"]/h1')

        title = driver.find_element_by_xpath('//*[@id="top_header"]/h1')
        assert 'iwaniska' in title.text.lower()

    def test_search_invalid(self):
        driver = self.driver
        driver.get(self.url + '/borough/search')
        self.wait_for(driver, By.ID, 'search')

        password_field = driver.find_element_by_id("search")
        password_field.clear()
        password_field.send_keys("a")

        driver.find_element_by_css_selector('#wrapper > borough-search > section > form > div:nth-child(2) > button').click()
        self.wait_for(driver, By.XPATH, '//*[@id="wrapper"]/borough-search/section/form/div[1]')

        alert = driver.find_element_by_xpath('//*[@id="wrapper"]/borough-search/section/form/div[1]')
        assert alert.text == 'Fraza musi mieć przynajmniej trzy znaki.'

    @staticmethod
    def get_results(driver):
        r = {}

        for i in range(1, 13):
            name = driver.find_element_by_xpath('//*[@id="wrapper"]/ng-component/results/section/table/tbody/tr['+str(i)+']/td[2]')
            wynik = driver.find_element_by_xpath('//*[@id="wrapper"]/ng-component/results/section/table/tbody/tr['+str(i)+']/td[3]')
            r[name.text] = (int(wynik.text.replace(',', '')))
        return r

    @staticmethod
    def compare_results(x, y):
        for name, value in x.items():
            assert y[name] == value

    def test_edit_circuit(self):
        def go_back(driver, results):
            driver.back()
            self.wait_for(driver, By.XPATH, '//*[@id="wrapper"]/ng-component/results/section/table/tbody/tr[1]/td[3]')
            borough_results = self.get_results(driver)
            self.compare_results(borough_results, results)

        results = []

        # log in
        driver = self.driver
        self.login(driver, 'mateusz', 'mateuszmateusz')
        self.wait_for(driver, By.ID, 'map')
        results.append(self.get_results(driver))

        driver.get(self.url + "/voivodeship/3")
        self.wait_for(driver, By.XPATH, '//*[@id="wrapper"]/ng-component/results/section/table/tbody/tr[1]/td[3]')
        results.append(self.get_results(driver))

        driver.find_element_by_xpath('//*[@id="wrapper"]/ng-component/pages/section/ul/li[2]/a').click()
        self.wait_for(driver, By.XPATH, '//*[@id="wrapper"]/ng-component/results/section/table/tbody/tr[1]/td[3]')
        results.append(self.get_results(driver))

        driver.find_element_by_xpath('//*[@id="wrapper"]/ng-component/pages/section/ul/li[2]/a').click()
        self.wait_for(driver, By.XPATH, '//*[@id="wrapper"]/ng-component/results/section/table/tbody/tr[1]/td[3]')
        results.append(self.get_results(driver))

        # go to circuit edition
        driver.find_element_by_xpath('//*[@id="circuits"]/table/tbody/tr[1]/td[2]/a').click()
        self.wait_for(driver, By.XPATH, '//*[@id="result_1"]')

        # edit circuit
        fields = driver.find_element_by_xpath('//*[@id="wrapper"]/edit/section/form/div[1]')
        candidate = fields.find_element_by_xpath('//label')
        value = fields.find_element_by_xpath('//div/input')
        changed_value = int(value.get_attribute('value')) + 1
        value.clear()
        value.send_keys(str(changed_value))

        candidate = candidate.text

        # update scraped results
        for result in results:
            result[candidate] += 1

        # save
        driver.find_element_by_xpath('//*[@id="wrapper"]/edit/section/form/div[13]/button').click()
        self.wait_for(driver, By.XPATH, '//*[@id="wrapper"]/edit/section/div')
        info = driver.find_element_by_xpath('//*[@id="wrapper"]/edit/section/div')
        assert info.text == 'Pomyślnie zapisano dane.'

        # go back with checking if data matches
        go_back(driver, results[-1])
        go_back(driver, results[-2])
        go_back(driver, results[-3])
        go_back(driver, results[-4])

    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()
