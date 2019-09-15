import json

file=open('nvdcve-1.0-2019.json','r')
data=json.load(file)

cves=data['CVE_Items']

print(len(cves))

print(cves[0].keys())