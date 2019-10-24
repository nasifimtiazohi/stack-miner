from difflib import SequenceMatcher
from dbconnection import *
conn=openConnection()
mapping={'Fedora30':'fc30','Fedora29':'fc29'}
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
def getEntry_PackageAndVersions(crashID,software):
    software=mapping[software]
    query='select component from crashes where crashID={}'.format(crashID)
    result=execute(query,conn)
    component=result[0]['component']

    query='''select * from relatedPackages
            where crashID={}
            and version like "%{}";'''.format(crashID,software)
    packages=execute(query,conn)

    dist=0
    target=None
    for item in packages:
        package=item['package']
        d=similar(component,package)
        if d>dist:
            dist=d
            target=package 
    print(crashID,software,target)
    #TODO: get this in the above pass?
    # query='''select version from relatedPackages 
    #         where crashID={} and package="{}"'''.format(crashID,target)
    # results=execute(query,conn)
    # versions=[]
    # for item in results:
    #     versions.append(item['version'])
    # return target,versions
    return target

def fillupEntryPackage(software):
    query='''select distinct c.crashID from crashes c
            join softwares s
            on c.crashID=s.crashID
            join relatedPackages r 
            on c.crashID =r.crashID
            where s.{}=1'''.format(software)
    crashIDs=execute(query,conn)

    for item in crashIDs:
        print(item['crashID'])
        package=getEntry_PackageAndVersions(item['crashID'],software)
        query='''insert into entryPackage values ({},"{}","{}")'''.format(item['crashID'],software,package)
        execute(query,conn)

if __name__=='__main__':
    fillupEntryPackage('Fedora30')

