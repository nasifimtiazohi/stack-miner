import json
import logger

file=open('nvdcve-1.0-2019.json','r')
data=json.load(file)

cves=data['CVE_Items']

print(len(cves))

print(cves[0].keys())

for cve in cves:
    id=cve['cve']['CVE_data_meta']['ID']

    affects=cve['cve']['affects']
    if len (affects) > 1:
        logger.warning("affects have more than one entry")
        print(cve)
        exit(1)
    vendors=affects['vendor']
    if len(vendors)>1:
        logger.warning("affects have more than one entry")
        print(cve)
        exit(1)
    vendors=vendors['vendor_data']

    #TODO get the list of products and here

    





    
    
    
    