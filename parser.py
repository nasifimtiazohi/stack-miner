import re
import traceback

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from logger import *

# Convenience Aliases
CLASS = By.CLASS_NAME
CSS = By.CSS_SELECTOR
ID = By.ID
TAG = By.TAG_NAME

# Date Parsing
DATE_RE = re.compile('(\d{4})-(\d{2})-(\d{2})')
YEAR_RE = re.compile('(\d{4})')


class Parser(object):
    def __init__(self, service, browser):
        self.service = service
        self.browser = browser
        self.driver = None

    def get_header(self):
        if self.service == 'fedora':
            return ('Crash_ID', 'Component', 'Crash Function', 'Status', 'Type', 'Last Date', 'First Date', 'Count')
        else:
            return None

    def parse(self, url):
        debug('Parsing {}'.format(url))
        if self.service == 'fedora':
            return self._parse_fedora(url)

    def setup(self):
        self.driver = self._get_driver(self.browser)

    def teardown(self):
        if self.driver:
            self.driver.close()

    def _get_driver(self, browser):
        driver = None

        if browser == 'firefox':
            driver = webdriver.Firefox()
        else:
            error('Cannot create driver for browser {}'.format(browser))
            sys.exit(1)

        return driver

    def _parse_fedora(self, url):
        _results = list()

        try:
            self.driver.get(url)
            results = self.driver.find_element(ID, 'report-list')
            for result in results.find_elements(CSS, 'tr'):
                line = list()
                for td_result in result.find_elements(CSS, 'td'):
                    line.append(td_result.text)
                    debug(td_result.text)

                if line:
                    _results.append(line)
        except WebDriverException:
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)

        return _results

    def _contains(self, element, by, value):
        elements = element.find_elements(by, value)
        return len(elements) > 0
