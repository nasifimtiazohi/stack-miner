import re
import traceback
import argparse
import csv
import sys
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from logger import *
from parser import Parser
import pymysql
import os 
import time
connection=None
def openConnection():
    global connection
    import getpass
    print("enter host name: ")
    HOST=input()
    print("enter user name: ")
    USER=input()
    print("enter password: ")
    PASSWD=getpass.getpass()
    connection = pymysql.connect(host=HOST,
                                port=3306,
                                user=USER,
                                password=PASSWD,
                                db='crashpatch',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor,
                                autocommit=True,
                                local_infile=True)
def execute(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        results=cursor.fetchall()
    return results

def init_parse_individual_crashes():
    count=0
    architecture=[]
    backtrace=[]
    report=[]
    os=[]
    relPackages=[]
    return count,architecture,backtrace,report,os,relPackages
def convert_to_int(s):
    if type(s)==str:
        s=s.strip().replace(',','')
    return int(s)
def load_List_into_Table(list,table):
    scriptname=os.path.basename(__file__)
    tempfile=scriptname+'_temp.csv'
    #warning: no headers in these lists
    with open(tempfile, 'w') as file_:
            writer = csv.writer(file_)
            writer.writerows(list)
    file_.close()
    query='''LOAD DATA LOCAL INFILE '{}' INTO TABLE crashpatch.{}
                FIELDS TERMINATED BY ',' 
                ENCLOSED BY '"' 
                LINES TERMINATED BY '\n' '''.format(tempfile,table)
    execute(query)
    os.remove(tempfile)
    print("loaded 1000 new data")
def loadCrashData(architecture,backtraces,report,os,relPackages):
    load_List_into_Table(report,'crashReport')
    load_List_into_Table(backtraces,'backtrace')
    load_List_into_Table(relPackages,'relatedPackages')
    load_List_into_Table(architecture,'architecture')
    load_List_into_Table(os,'os')
def putIfValueFound(d,key):
    if key in d.keys():
        return d[key]
    else:
        return r'\N'
def convert_report_to_dbRow(crashID,dict):
    l=[None]*9
    l[0]=crashID
    try:
        l[1]=convert_to_int(dict['Problem'])
    except:
        l[1]=r'\N'
    l[2]=putIfValueFound(dict,'Executable')
    l[3]=putIfValueFound(dict,'Error name')
    l[4]=putIfValueFound(dict,'Created')
    l[5]=putIfValueFound(dict,'Last change')
    l[6]=putIfValueFound(dict,'Unique reports')
    if l[6]!=r'\N':
        l[6]=convert_to_int(l[6])
    l[7]=putIfValueFound(dict,'External bugs')
    l[8]=putIfValueFound(dict,'Tainted')
    return l
def convert_backtraces_to_dbrow(id,backtraces):
    for b in backtraces:
        b.insert(0,id)
        try:
            b[-1]=convert_to_int(b[-1])
        except:
            b[-1]= 0
    return backtraces
def add_id_and_convert_to_dbrow(id,results):
    for temp in results:
        temp.insert(0,id)
    return results
#TODO: a whole of refactoring can be done here by using class object of each crash
def parse_individual_crashes(crashIDs):
    #initialize the browser drive
    parser = Parser()
    parser.setup()
    # initialize after every 20,000 load into database
    count,architecture,backtraces,report,os,relPackages=init_parse_individual_crashes() 
    for crashID in crashIDs:
        id=crashID['crashID']
        #do all mining and appending to the lists
        # '_' prefix means a dictionary which we need to convert into a table row
        url='https://retrace.fedoraproject.org/faf/reports/'+str(id)
        _architecture,_backtraces,_report,_os,_relPackages=parser.parse_crash_report(url)
        if not _report:
            continue
        report.append(convert_report_to_dbRow(id,_report))
        backtraces+=convert_backtraces_to_dbrow(id,_backtraces)
        relPackages+=add_id_and_convert_to_dbrow(id,_relPackages)
        architecture+=add_id_and_convert_to_dbrow(id,_architecture)
        os+=add_id_and_convert_to_dbrow(id,_os)
        count +=1
        if count > 1000:
            loadCrashData(architecture,backtraces,report,os,relPackages)
            count,architecture,backtraces,report,os,relPackages=init_parse_individual_crashes() 
    #load he remaining data 
    loadCrashData(architecture,backtraces,report,os,relPackages)
    #end function by closing the browser
    parser.teardown()
if __name__=='__main__':
    parser = argparse.ArgumentParser(
            description=(
                'Script to collect data for individual crashes.'
            )
        )
    parser.add_argument(
            '--start', dest='start', type= int,  default=1000000,
            help='The count of new crash IDs to mine'
        )
    parser.add_argument(
            '--stop', dest='stop', type= int,  default=1000000,
            help='The count of new crash IDs to mine'
        )
    args = parser.parse_args()


    openConnection()
    #set local infile on in case it's off
    query='set global local_infile=1;'
    execute(query)

    #get new crash IDs to mine
    query='''select crashID from crashes 
            where crashID not in 
            (select crashID from crashReport)
            -- order by rand()
            and crashID > {}
            and crashID < {}'''.format(args.start,args.stop)
    crashIDs=execute(query)

    parse_individual_crashes(crashIDs)


        