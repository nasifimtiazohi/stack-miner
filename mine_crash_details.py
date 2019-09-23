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
import datetime
import gc
import os as libraryOS
import psutil
from dbconnection import *
connection=openConnection()
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
    execute(query,connection)
    os.remove(tempfile)
def loadCrashData(architecture,backtraces,report,os,relPackages):
    load_List_into_Table(report,'crashReport')
    load_List_into_Table(backtraces,'backtrace')
    load_List_into_Table(relPackages,'relatedPackages')
    load_List_into_Table(architecture,'architecture')
    load_List_into_Table(os,'os')
    print('loaded ',len(report),' new data')
    print(datetime.datetime.now())
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
        #print('count currently stands at: ',count)
        count +=1
        if count > 50:
            process = psutil.Process(libraryOS.getpid())
            print('BEFORE DUMPING: ',process.memory_info().rss)
            loadCrashData(architecture,backtraces,report,os,relPackages)
            count,architecture,backtraces,report,os,relPackages=init_parse_individual_crashes() 
            gc.collect()
            process = psutil.Process(libraryOS.getpid())
            print('AFTER DUMPING: ',process.memory_info().rss)
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
        '--software',dest='software',type=str,
        help='The version of software to fetch crash details'
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



    #get new crash IDs to mine
    query='''select c.crashID from crashes c
            join softwares s
            on c.crashID=s.crashID
            where s.{}=1 and
            c.crashID not in 
            (select crashID from crashReport)
            -- order by rand()
            and c.crashID > {}
            and c.crashID < {}'''.format(args.software,args.start,args.stop)
    crashIDs=execute(query,connection)
    print("this script will fetch ",len(crashIDs), " crashes")
    parse_individual_crashes(crashIDs)


        