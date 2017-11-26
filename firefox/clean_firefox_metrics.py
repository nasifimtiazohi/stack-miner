import subprocess, csv

metricContents = {}

with open('/Users/christophertheisen/research/vpm_comparison/firefox_metrics.csv', 'rU') as csvdata:
  fieldnames = ['CountClassBase','CountClassCoupled','CountClassDerived','CountDeclInstanceVariablePrivate','CountDeclMethod','CountInput','CountLine','CountOutput','Cyclomatic','MaxInheritanceTree','MaxNesting']

  reader = csv.DictReader(csvdata)
  next(reader)
  for row in reader:
    if row['File'] in metricContents:
      for fields in fieldnames:
        try: 
          metricContents[row['File']][fields] += int(row[fields])
        except:
          True
    else:
      metricContents[row['File']] = {}
      for fields in fieldnames:
        try: 
          metricContents[row['File']][fields] = int(row[fields])
        except ValueError:
          metricContents[row['File']][fields] = 0

with open('clean_firefox_metrics.csv', 'wb') as csv_file:
    csv_file.write('File,CountClassBase,CountClassCoupled,CountClassDerived,CountDeclInstanceVariablePrivate,CountDeclMethod,CountInput,CountLine,CountOutput,Cyclomatic,MaxInheritanceTree,MaxNesting\n')
    for key, value in metricContents.items():
      csv_file.write(key)
      for subkey, subvalue in value.items():
        csv_file.write(',' + str(subvalue))
      csv_file.write('\n')


