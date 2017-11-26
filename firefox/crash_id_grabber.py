import requests, json, os, time


#for i in range(0, 1000000, 200):
for i in range(0, 50000, 200):
	
	writer = open("november_crashes_1/crashes_" + str(i) + '_' + str(i+200) + '.csv', "w+")

	url = 'https://crash-stats.mozilla.com/api/SuperSearch/?release_channel=nightly&_results_offset=' + str(i) + '&_results_number=200&date=%3C2017-11-01'
	print "Grabbing " + str(i) + " through " + str(i+200)
	try:
		payload = requests.get(url).json()
		try:
			for frames in payload['hits']:
				if 'uuid' in frames:
					writer.write(frames['uuid'])
					writer.write('\n')
		except:
			print "Failed to parse crash."

	except:
		print "Request failed: wait a bit for next"
		time.sleep(3)

	writer.close()