import pymysql
import keyring
import getpass
import os
credential={}


def openConnection():
    global credential
    print("enter host name: ")
    credential['host']=input()
    print("enter user name: ")
    credential['user']=input()
    print("enter password: ")
    keyring.set_password(os.path.basename(__file__),credential['user'],getpass.getpass())
    connection = pymysql.connect(host=credential['host'],
                                port=3306,
                                user=credential['user'],
                                password=keyring.get_password(os.path.basename(__file__),credential['user']),
                                db='crashpatch',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor,
                                autocommit=True,
                                local_infile=True)
    return connection

def execute(query,connection):
    with connection.cursor() as cursor:
        cursor.execute(query)
        results=cursor.fetchall()
    return results

def executemany(query,connection):
    query=query.replace('\n','')
    queries=query.split(';')
    if queries[-1].strip()=='':
        queries=queries[:-1]
    for q in queries:
        execute(q.strip(),connection)

def reconnect():
    connection = pymysql.connect(host=credential['host'],
                                port=3306,
                                user=credential['user'],
                                password=keyring.get_password(os.path.basename(__file__),credential['user']),
                                db='crashpatch',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor,
                                autocommit=True,
                                local_infile=True)
    return connection