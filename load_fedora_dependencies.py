import pymysql
import cryptography
import os
import csv
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
print("enter file name: ")
file=input()
print("enter table name: ")
table=input()
''' table should have 5 columns. 
package's name, architecture, version, release, and base'''

scriptname=os.path.basename(__file__)
tempfile=scriptname+'_temp.csv'

rows=[]

with open(file,'r') as fp:
    line=fp.readline()
    while line:
        if not ('Last metadata expiration check' in line or 'Installed Packages' in line or 'Available Packages' in line):
            print(line)
            line=line.split()
            temp=line[0].split('.')
            name=temp[0]
            architecture=temp[1]
            temp=line[1].split('-')
            version=temp[0]
            release=temp[1]
            base=line[2]
            rows.append([name,architecture,version,release,base])
        line=fp.readline()


with open(tempfile, 'w') as file_:
    writer = csv.writer(file_)
    writer.writerows(rows)

query='''LOAD DATA LOCAL INFILE '{}' INTO TABLE crashpatch.{}
                FIELDS TERMINATED BY ',' 
                ENCLOSED BY '"' 
                LINES TERMINATED BY '\n' '''.format(tempfile,table)

connection=openConnection()
with connection.cursor() as cursor:
    cursor.execute(query)


