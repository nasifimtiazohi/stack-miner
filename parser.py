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
    def convert_to_int(self,s):
        s=s.strip().replace(',','')
        return int(s)
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
        try:
            container=self.driver.find_element_by_css_selector('body > div.container-fluid > div > div.row > div:nth-child(1) > dl')
            dts=container.find_elements_by_tag_name('dt')
            dds=container.find_elements_by_tag_name('dd')
            #TODO: assert if length of dts and dds are equal
            for i in range(0,len(dds)):
                _report[dts[i].text]=dds[i].text
            if 'Tainted' in container.get_attribute('innerHTML'):
                _report['Tainted']='Tainted'
        except:
            print('could not locate general report for ',self.driver.current_url)
        return _report
    def get_backtraces(self):
        backtraces=[]
        try:
            #do mining
            container=self.driver.find_element_by_css_selector('body > div.container-fluid > div > table > tbody')
            rows=container.find_elements_by_tag_name('tr')
            for row in rows:
                backtrace=[]
                for col in row.find_elements_by_tag_name('td'):
                    backtrace.append(col.text)
                backtraces.append(backtrace)
        except:
            print('could not locate backtraces for ',self.driver.current_url)
        return backtraces
    def get_packages(self):
        packages=[]
        try:
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
                    count=self.convert_to_int(temp[1].text)
                    packages.append([package,version,count])
        except:
            print('could not locate related packages for ',self.driver.current_url)
        return packages
    def get_os(self):
        os=[]
        try:
            container=self.driver.find_element_by_css_selector('body > div.container-fluid > div > div.row > div.col-md-6.statistics > div.unique_data > table > tbody')
            soup=bs(container.get_attribute('innerHTML'),'html.parser')
            rows=soup.find_all('tr',{'class':['package','package hide']})
            for row in rows:
                cols=row.find_all('td')
                package=cols[0].text
                temp=cols[1].text.split('/')
                uniqueCount=self.convert_to_int(temp[0])
                totalCount=self.convert_to_int(temp[1])
                os.append([package,uniqueCount,totalCount])
        except:
            print('could not locate os for ',self.driver.current_url)
        return os
    def get_architectures(self):
        arch=[]
        try:
            container=self.driver.find_element_by_css_selector('body > div.container-fluid > div > div.row > div.col-md-6.statistics > table.table.table-striped.table-bordered.metric.table-condensed > tbody')
            soup=bs(container.get_attribute('innerHTML'),'html.parser')
            rows=soup.find_all('tr',{'class':['package','package hide']})
            for row in rows:
                cols=row.find_all('td')
                architecture=cols[0].text
                count=self.convert_to_int(cols[1].text)
                arch.append([architecture,count])
        except:
            print('could not architecture for ',self.driver.current_url)
        return arch
    def parse_crash_report(self,url):
        try:
            self.driver.get(url)
            #get the reports
            _report=self.get_general_report()
            _backtraces=self.get_backtraces()
            _os=self.get_os()
            _architecture=self.get_architectures()
            _relPackages=self.get_packages()
        except WebDriverException:
            extype, exvalue, extrace = sys.exc_info()
            traceback.print_exception(extype, exvalue, extrace)
            print('could not load page?:',url)
            return [],[],[],{},[]
        
        return _architecture,_backtraces,_report,_os,_relPackages
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
