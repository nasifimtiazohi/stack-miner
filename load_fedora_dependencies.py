import pymysql
import cryptography
import os
import csv
from dbconnection import *
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
    id=1
    while line:
        if not ('Last metadata expiration check' in line or 'Installed Packages' in line or 'Available Packages' in line):
            line=line.split()
            temp=line[0].split('.')
            name=temp[0].strip()
            architecture=temp[1].strip()
            temp=line[1].split('-')
            version=temp[0].strip()
            release=temp[1].strip()
            base=line[2].strip()
            rows.append([id,name,architecture,version,release,base])
        line=fp.readline()
        id+=1


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


