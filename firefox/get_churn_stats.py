w = open('churn_stats_withtotal.csv','w')

import subprocess

TraceContents = {}

with open('/Users/christophertheisen/research/vpm_comparison/file_list_test.csv', 'rU') as f:
  for line in f:
      myLine = line.split(',')
      TraceContents[myLine[0].strip()] = {'churn':0, 'churnTotal':0, 'unique':0}


print "finished putting into initial dict"

i = 0
        
for x in TraceContents:
  newMetrics = {}
  churn = 0
  uniques = 0

  p = subprocess.Popen('hg log -d \"jun 2017 to nov 2017\" firefox/' + x, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  for line in p.stdout.readlines():
    if "user:" in line:
      name = line.split(':')[1].rstrip().lstrip()
      if name in newMetrics:
          churn += 1
      else:
          newMetrics[name] = 1
          churn += 1
          uniques += 1

  churnTotal = 0

  p = subprocess.Popen('hg churn -d \"jun 2017 to nov 2017\" firefox/' + x, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  for line in p.stdout.readlines():
    newLine = line.split()
    try:
      churnTotal += int(newLine[1])
    except:
      churnTotal += 1

  TraceContents[x]['churn'] = churn
  TraceContents[x]['unique'] = uniques
  TraceContents[x]['churnTotal'] = churnTotal
  
  i += 1
  if i % 10 == 0:
    print 'Parsed ', i, ' lines.'

for x in TraceContents:
    w.write(x + ',' + str(TraceContents[x]['churn']) + ',' + str(TraceContents[x]['churnTotal']) + ',' + str(TraceContents[x]['unique']) + '\n')
    
    
#retval = p.wait()

