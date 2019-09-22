import pymysql

def openConnection():
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
