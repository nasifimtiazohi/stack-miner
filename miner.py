import argparse
import csv
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from logger import *
from parser import Parser

import pymysql
import os 
connection = pymysql.connect(host='localhost',
                             user='root',
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
def executemany(query):
    query=query.replace('\n','')
    queries=query.split(';')
    if queries[-1].strip()=='':
        queries=queries[:-1]
    for q in queries:
        execute(q.strip())
def loadCrashIds(results,software):
    scriptname=os.path.basename(__file__)
    tempfile=scriptname+'_temp.csv'
    #TODO: prefix temp table name with the script name so that multiple scripts
        # run together do not conflict. 
    with open(tempfile, 'w') as file_:
            writer = csv.writer(file_)
            writer.writerows(results)
    file_.close()

    #create a temporary table for keeping track of exisiting crashes to new software
    query='''drop table if exists temp;
            create table temp as
            select * from crashes limit 0;
            alter table temp add primary key (crashID);'''
    executemany(query)

    # load the crash data into temp table
    query='''LOAD DATA LOCAL INFILE '{}' INTO TABLE crashpatch.temp
                FIELDS TERMINATED BY ',' 
                ENCLOSED BY '"' 
                LINES TERMINATED BY '\n' 
                IGNORE 1 LINES'''.format(tempfile)
    execute(query)

    #insert the new ids to crashes table 
    query='''insert into crashes 
        select * from temp
        where crashID not in (select crashID from crashes) ;'''
    execute(query)

    #update the exisiting ones
    query='''update softwares
            set {}=1
            where crashID in 
            (select * from
            (select s.crashID as crashID from temp t
            join softwares s on s.crashID=t.crashID)as sub);'''.format(software)
    execute(query)
    #put the new ones to software
    query='''insert into softwares(crashId,{})
            select crashId, 1 from temp
            where crashID not in (select crashID from softwares);'''.format(software)
    execute(query)
    
    #clean the temporary tables and csv files
    os.remove(tempfile)
    query='drop table temp;'
    execute(query)
def parse(service, url, start, stop, browser, software):
    results = list()
    if '{}' not in url:
        warning('URL does not have a placeholder for page number.')

    try:
        parser = Parser(service, browser)
        parser.setup()

        header = parser.get_crashes_header()
        if header:
            results.append(header)

        index = 0
        for page in range(start, stop+1, 40):
            temp=parser.parse_crashes(url.format(page))
            if not temp:
                print("no new data found at page ",page,"...exiting..")
                return True
            results += temp
            info('{} results after {}\'th offset(s)'.format(len(results) - 1, index))
            if len(results) >  1000:
                loadCrashIds(results,software)
                results=[]
            index += 40
    except KeyboardInterrupt:
        sys.stdout.write('\r')
        info('Exiting...')
        return False
    finally:
        #insert the rest of the data in database
        if results:
            loadCrashIds(results,software)
        parser.teardown()

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description=(
                'Script to collect crash dump stack traces.'
            )
        )
    parser.add_argument(
            '-b', dest='browser', default='firefox',
            choices=['firefox'],
            help='The browser to use when retrieving the search results.'
        )
    parser.add_argument(
            '--start', dest='start', type=int, default=1,
            help='Index of the page of results to start parsing from.'
        )
    parser.add_argument(
            '--stop', dest='stop', type=int, default=1,
            help='Index of the page of results to stop parsing to.'
        )

    parser.add_argument(
            '--software', dest='software', type=str, default=1,
            help='The specific version of software the crash dump will belong to.'
        )

    parser.add_argument(
            'service',
            choices=['fedora'],
            help=(
                'The crash dump stack trace source from which the results are to be parsed.'
            )
        )
    parser.add_argument(
            'url',
            help=(
                'The URL of the search results. Use {} as the placeholder for '
                'page number.'
            )
        )
    # parser.add_argument(
    #         'output', help=(
    #             'Path to the file to which the parse results should be '
    #             'written.'
    #         )
    #     )
    args = parser.parse_args()

    #set local infile on in case it's off
    query='set global local_infile=1;'
    execute(query)
    
    #check if software is listed in the database
    software=args.software
    query='''Select Column_Name
               From INFORMATION_SCHEMA.COLUMNS
               Where Table_Name = 'softwares' and Column_Name = '{}' '''.format(software)
    if not execute(query):
        error('software version is not listed to process')
        exit()

    info('Parsing {}'.format(args.url))
    exit = parse(
            args.service, args.url, args.start, args.stop, args.browser, args.software
        )
    print(exit)

    # if results:
    #     with open(str(args.start)+"_"+str(args.stop)+"_"+args.output, 'w') as file_:
    #         writer = csv.writer(file_)
    #         writer.writerows(results)
    # info('Results written to {}'.format(args.output))
