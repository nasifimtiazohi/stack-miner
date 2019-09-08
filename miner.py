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
                             db='coverityscan',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor,
                             autocommit=True,
                             local_infile=True)
def loadDatabase(results, table):
    with open("temp.csv", 'w') as file_:
            writer = csv.writer(file_)
            writer.writerows(results)
    file_.close()
    query='''LOAD DATA LOCAL INFILE 'temp.csv' INTO TABLE crashpatch.{}
                FIELDS TERMINATED BY ',' 
                ENCLOSED BY '"' 
                LINES TERMINATED BY '\n'
                IGNORE 1 LINES;'''.format(table)
    with connection.cursor() as cursor:
        cursor.execute(query)
    os.remove("temp.csv")
def parse(service, url, start, stop, browser):
    results = list()
    debug=[]
    if '{}' not in url:
        warning('URL does not have a placeholder for page number.')

    try:
        parser = Parser(service, browser)
        parser.setup()

        header = parser.get_header()
        if header:
            results.append(header)

        index = 0
        for page in range(start, stop+1, 40):
            temp=parser.parse(url.format(page))
            if not temp:
                print("no new data found at page ",page,"...exiting..")
                return True
            results += temp
            info('{} results after {}\'th offset(s)'.format(len(results) - 1, index))
            if len(results) >  20000:
                loadDatabase(results,'crashes')
                results=[]
            index += 40
    except KeyboardInterrupt:
        sys.stdout.write('\r')
        info('Exiting...')
        return False
    finally:
        #insert the rest of the data in database
        if results:
            loadDatabase(results,'crashes')
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
    parser.add_argument(
            'output', help=(
                'Path to the file to which the parse results should be '
                'written.'
            )
        )
    args = parser.parse_args()

    info('Parsing {}'.format(args.url))
    exit = parse(
            args.service, args.url, args.start, args.stop, args.browser
        )
    print(exit)
    # if results:
    #     with open(str(args.start)+"_"+str(args.stop)+"_"+args.output, 'w') as file_:
    #         writer = csv.writer(file_)
    #         writer.writerows(results)
    # info('Results written to {}'.format(args.output))
