import pymysql
import pymongo
from dbconnection import *

'''
RQ1: What percenate of packages crash at least once 
and how many historically vulnerable packages are included in that subest of crashing packages?
'''

'''
Methodology:
step 1: Get the list of dependencies for the system
'''

def get_dependecies():
    query='''select distinct name,version
        from Fedora30_dependencies'''

