'''this script gives some descriptive stat for collected data'''
from dbconnection import *
from parseEntryPackage import *
conn=openConnection()

def crashCount():
    softwares=['Fedora30','Fedora29']
    rows=[]
    for software in softwares:
        '''Crashes valid only when we have a package field associate '''
        query='''select count(distinct c.crashID) as res 
                from crashes c
                join softwares s
                on c.crashID=s.crashID
                join relatedPackages r 
                on c.crashID =r.crashID
                where s.{}=1;'''.format(software)
        uniqueCrashes=execute(query,conn)[0]['res']
        uniqueCrashes='{:,}'.format(uniqueCrashes)

        query='''select sum(count) as res
                from (select distinct c.crashID, c.count from crashes c
                join softwares s
                on c.crashID=s.crashID
                join relatedPackages r 
                on c.crashID =r.crashID
                where s.{}=1) as sub'''.format(software)
        totalCrashes=execute(query,conn)[0]['res']
        totalCrashes='{:,}'.format(totalCrashes)

        rows.append([software,uniqueCrashes,totalCrashes])
        
    for row in rows:
        s='&'.join(str(col) for col in row)
        print(s,r'\\')
          

def crashingPackageCount():
    softwares=['Fedora30','Fedora29']
    rows=[]
    for software in softwares:
        query='''select count(distinct c.component) as res from crashes c
                        join softwares s
                        on c.crashID=s.crashID
                        join relatedPackages r 
                        on c.crashID =r.crashID
                        where s.{}=1'''.format(software)
        uniqueEntryPackages=execute(query,conn)[0]['res']
        uniqueEntryPackages='{:,}'.format(uniqueEntryPackages)
        
        query='''select count(distinct concat(package,version)) as res 
                from entryPackage c
                join softwares s
                on c.crashID=s.crashID
                where s.{}=1'''.format(software)
        uniqueEntryPackageVersions=execute(query,conn)[0]['res']
        uniqueEntryPackageVersions='{:,}'.format(uniqueEntryPackageVersions)
        
        rows.append([software,uniqueEntryPackages,uniqueEntryPackageVersions])

    for row in rows:
        s='&'.join(str(col) for col in row)
        print(s,r'\\')
def fillupEntryPackage():
    query='''select distinct c.crashID from crashes c
                        join softwares s
                        on c.crashID=s.crashID
                        join relatedPackages r 
                        on c.crashID =r.crashID'''
    crashIDs=execute(query,conn)
    #create an empty table to store the package names and the versions
    query='''create table entryPackage(
            crashID INT,
            package VARCHAR(255),
            version VARCHAR(255)
    );'''
    execute(query,conn)
    for item in crashIDs:
        print(item['crashID'])
        package,versions=getEntry_PackageAndVersions(item['crashID'],conn)
        for version in versions:
            query='''insert into entryPackage values ({},"{}","{}")'''.format(item['crashID'],package,version)
            print(query)
            execute(query,conn)

if __name__=='__main__':
    crashingPackageCount()