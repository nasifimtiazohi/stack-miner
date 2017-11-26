import subprocess, csv

file_list = {}
vuln_file_list = {}

with open('/Users/christophertheisen/research/vpm_comparison/unique_vulns.csv', 'rU') as csvdata:
  reader = csv.DictReader(csvdata)
  for row in reader:
    vuln_file_list[row['File']] = 1


with open('/Users/christophertheisen/research/vpm_comparison/copy_firefox_files.csv', 'rU') as csvdata:
  reader = csv.DictReader(csvdata)
  for row in reader:
    if row['File'] in vuln_file_list:
      file_list[row['File']] = 1
      vuln_file_list[row['File']] = 0
    else:
      file_list[row['File']] = 0



with open('clean_vuln_metrics.csv', 'wb') as csv_file:
  writer = csv.writer(csv_file)
  for key, value in file_list.items():
    writer.writerow([key, value])

i = 0

for key, value in vuln_file_list.items():
  if value == 1:
    print key
    i += 1

print 'num no metrics:' + str(i)


