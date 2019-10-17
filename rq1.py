import pymysql
import pymongo
import pandas as pd
from dbconnection import *
conn=openConnection()
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
    

def get_crash_count_percentiles():
    query='''select c.component, sum(c.count) as totalCrashes
            from crashes c
            join softwares s 
            on c.crashID=s.crashID
            where s.Fedora30=1
            group by c.component;'''
    results=execute(query,conn)
    df=pd.DataFrame(results)
    df.totalCrashes=df.totalCrashes.astype(int)
    percentiles=[]
    for i in range(0,100,10):
        percentiles.append(i/100)
    percentiles+=[.95,.99,1]
    print(percentiles)
    ret=[]
    for p in percentiles:
        ret.append(df.totalCrashes.quantile(p))
    return ret

def get_PC(percentiles):
    #get total packages
    

if __name__=='__main__':
    percentiles=get_crash_count_percentiles()
    print(percentiles)