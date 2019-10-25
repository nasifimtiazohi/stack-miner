import pymysql
import pymongo
import pandas as pd
from dbconnection import *
conn=openConnection()
'''
RQ1: What percentage of packages crash at least once 
and how many historically vulnerable packages are included in that subest of crashing packages?
'''

'''
Methodology:
step 1: Get the list of dependencies for the system
Step 2: See how of them were vulnerable 
        #package names case-sensitive?
        #
'''

# why the latest version of some packages are not available in fedora rpm

def identify_vulnerable_dependencies(software):
    
    query='''select * from {software}_dependencies
            where id not in (select id from {software}_vuln_dependencies);'''.format(software=software)
    results=execute(query,conn)
    for item in results:
        id=item['id']
        package=item['package']
        version=item['version']
        query='''select * from affected_products
                where product_name='{}'
                and version_value='{}';'''.format(package,version)
        temp=execute(query,conn)
        print(id)
        if len(temp)>0:
            query='''insert into {}_vuln_dependencies values({},{})'''.format(software,id,1)
        else:
            query='''insert into {}_vuln_dependencies values({},{})'''.format(software,id,0)
        execute(query,conn)

    

def analysis(software):
    query='''select count(distinct package,version) as c
                from {}_dependencies;'''.format(software)
    totalPackages=execute(query,conn)[0]['c']
    query='''select distinct t1.package,t1.version,sum(count) as totalCrashes
                from Fedora30_dependencies fd
                join
                (select rP.crashID, rP.package, rP.version, rP.count
                from entryPackage eP
                join relatedPackages rP
                    on eP.crashID = rP.crashID
                    and eP.package=rP.package
                where eP.software="Fedora30") as t1
                on fd.package=t1.package
                where t1.version like concat('%',fd.version,'%')
                group by t1.package, t1.version;'''
    results=execute(query,conn)
    df=pd.DataFrame(results)
    df.totalCrashes=df.totalCrashes.astype(int)
    percentiles=[]
    for i in range(0,100,10):
        percentiles.append(i/100)
    percentiles+=[.95,.99,1]
    crashes=[]
    for p in percentiles:
        crashes.append(df.totalCrashes.quantile(p))
    PC=[]
    for c in crashes:
        PC.append((df.totalCrashes >= c).sum())
    
    query='''select distinct t1.package,t1.version,sum(count) as totalCrashes
            from
                (select fd.id,fd.package,fd.version from {software}_dependencies fd
                join {software}_vuln_dependencies fvd
                    on fd.id=fvd.id
                    where vuln=1) t2
            join
            (select rP.crashID, rP.package, rP.version, rP.count
            from entryPackage eP
            join relatedPackages rP
                on eP.crashID = rP.crashID
                and eP.package=rP.package
            where eP.software="{software}") as t1
            on t2.package=t1.package
            where t1.version like concat('%',t2.version,'%')
            group by t1.package, t1.version;'''.format(software=software)
    results=execute(query,conn)
    vdf=pd.DataFrame(results)
    query='''select count(distinct package,version) as c
            from {software}_dependencies fd
            join {software}_vuln_dependencies fvd
            on fd.id=fvd.id
            where vuln=1'''.format(software=software)
    totalVuln=execute(query,conn)[0]['c']
    VPC=[]
    for c in crashes:
        VPC.append((vdf.totalCrashes>=c).sum())
    print(totalPackages,totalVuln)
    for i in range(0,len(percentiles)):
        temp=[int(percentiles[i]*100),round(crashes[i],1)]
        temp.append(str(PC[i])+' ('+ str(round(float(PC[i])/float(totalPackages)*100,1))+r'\%)')
        temp.append(str(VPC[i])+' ('+ str(round(float(VPC[i])/float(totalVuln)*100,1))+r'\%)')
        print('&'.join(str(x) for x in temp)+r'\\')
        
def get_PC(percentiles):
    pass
    

if __name__=='__main__':
    analysis("Fedora29")