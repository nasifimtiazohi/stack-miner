'''this script gives some descriptive stat for collected data'''
from dbconnection import *
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
        query='''select count(distinct package) as res
                    from entryPackage
                    where software="{}";'''.format(software)
        uniqueEntryPackages=execute(query,conn)[0]['res']
        uniqueEntryPackages='{:,}'.format(uniqueEntryPackages)
        print(uniqueEntryPackages)
        query='''select count(distinct rP.package, rP.version) as res
                from entryPackage eP
                join relatedPackages rP
                    on eP.crashID = rP.crashID
                    and eP.package=rP.package
                where software="{}"'''.format(software)
        uniqueEntryPackageVersions=execute(query,conn)[0]['res']
        uniqueEntryPackageVersions='{:,}'.format(uniqueEntryPackageVersions)
        
        rows.append([software,uniqueEntryPackages,uniqueEntryPackageVersions])

    for row in rows:
        s='&'.join(str(col) for col in row)
        print(s,r'\\')

def manually_installed():
    softwares=['Fedora30','Fedora29']
    rows=[]
    for software in softwares:
        query='''select count(distinct package) as res
                    from entryPackage
                    where software="{software}"
                    and package not in
                    (select package from {software}_dependencies);'''.format(software=software)
        packages=execute(query,conn)[0]["res"]
        packages='{:,}'.format(packages)

        query='''select count(*)
                    from
                    (select distinct rP.package,rP.version
                    from entryPackage eP
                    join relatedPackages rP
                        on eP.crashID = rP.crashID
                        and eP.package=rP.package
                    where eP.software="{software}") as t1
                    where not exists(
                        select * from {software} fd
                        where t1.package=fd.package
                        and t1.version=fd.version
                        );'''.format(software=software)
        version=execute(query,conn)[0]["res"]
        version='{:,}'.format(version)
        
        rows.append([software,packages,version])
    for row in rows:
        s='&'.join(str(col) for col in row)
        print(s,r'\\')    



if __name__=='__main__':
    manually_installed()