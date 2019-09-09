import re
import traceback
import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup as bs
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
    def __init__(self, service='fedora', browser='firefox'):
        self.service = service
        self.browser = browser
        self.driver = None

    def get_crashes_header(self):
        if self.service == 'fedora':
            return ('Crash_ID', 'Component', 'Crash Function', 'Status', 'Type', 'Last Date', 'First Date', 'Count')
        else:
            return None

    def parse_crashes(self, url):
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
            driver = webdriver.Firefox(executable_path='./geckodriver')
            driver.set_page_load_timeout(300)
        else:
            error('Cannot create driver for browser {}'.format(browser))
            sys.exit(1)

        return driver
    def get_general_report(self):
        _report={}
        container=self.driver.find_element_by_css_selector('body > div.container-fluid > div > div.row > div:nth-child(1) > dl')
        dts=container.find_elements_by_tag_name('dt')
        dds=container.find_elements_by_tag_name('dd')
        #TODO: assert if length of dts and dds are equal
        for i in range(0,len(dds)):
            _report[dts[i].text]=dds[i].text
        if 'Tainted' in container.get_attribute('innerHTML'):
            _report['Tainted']='Tainted'
        return _report
    def get_backtraces(self):
        backtraces=[]
        #do mining
        container=self.driver.find_element_by_css_selector('body > div.container-fluid > div > table > tbody')
        rows=container.find_elements_by_tag_name('tr')
        for row in rows:
            backtrace=[]
            for col in row.find_elements_by_tag_name('td'):
                backtrace.append(col.text)
            backtraces.append(backtrace)
        return backtraces
    def get_packages(self):
        packages=[]
        container=self.driver.find_element_by_css_selector('body > div.container-fluid > div > div.row > div.col-md-6.statistics > table.table.table-bordered.counts-table.table-condensed > tbody')
        soup=bs(container.get_attribute('innerHTML'),'html.parser')
        rows=soup.find_all('tr',{'class':['package','package stripe','package hide','package stripe hide','version','version hide']})
        #we will have a package name updated first before getting a version
        package=''
        for row in rows:
            if 'package' in row['class']:
                temp=row.find_all('td')
                package=temp[0].text.strip()
            elif 'version' in row['class']:
                temp=row.find_all('td')
                version=temp[0].text.strip()
                count=temp[1].text.strip()
                packages.append([package,version,count])
        return packages
    def parse_crash_report(self,url):
        _architecture=[]
        _backtrace=[]
        _report={}
        _os=[]
        _relPackages=[]
        try:
            self.driver.get(url)
            #get the reports
            _report=self.get_general_report()
            _backtraces=self.get_backtraces()
            _relPackages=self.get_packages()
        except WebDriverException:
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace) 
        
        return _report,_backtraces,_relPackages
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
