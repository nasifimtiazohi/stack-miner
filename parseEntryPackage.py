from difflib import SequenceMatcher
from dbconnection import *

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
def getEntry_PackageAndVersions(crashID,conn):
    query='select component from crashes where crashID={}'.format(crashID)
    result=execute(query,conn)
    component=result[0]['component']

    query='select * from relatedPackages where crashID={}'.format(crashID)
    packages=execute(query,conn)

    dist=0
    target=None
    for item in packages:
        package=item['package']
        d=similar(component,package)
        if d>dist:
            dist=d
            target=package 
    #TODO: get this in the above pass?
    query='''select version from relatedPackages 
            where crashID={} and package="{}"'''.format(crashID,target)
    results=execute(query,conn)
    versions=[]
    for item in results:
        versions.append(item['version'])
    return target,versions

if __name__=='__main__':
    pass

