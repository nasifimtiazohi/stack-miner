import requests, json, os, time

start = 0
end = 1

crash_files = os.listdir('/Users/christophertheisen/research/vpm_comparison/parsers/october_crashes_5')

for files in crash_files:
	
	reader = open('october_crashes_5/' + files, "r")
	print 'Parsing file: ' + files

	for line in reader:
		tryAlt = 0

		crash_id = line.rstrip()

		writer = open("october_files_5/crash_" + str(crash_id) + ".csv", 'w')

		print "Getting crash_id = " + str(crash_id)

		url = 'https://crash-stats.mozilla.com/api/ProcessedCrash/?crash_id=' + crash_id + '&datatype=processed'
		try:
			payload = requests.get(url).json()
			try:
				for frames in payload['upload_file_minidump_browser']['json_dump']['crashing_thread']['frames']:
					if 'file' in frames:
						writer.write(frames['file'])
						writer.write('\n')
			except:
				tryAlt = 1

			if tryAlt == 1:
				try:
					for frames in payload['json_dump']['crashing_thread']['frames']:
						if 'file' in frames:
							writer.write(frames['file'])
							writer.write('\n')
				except:
					print "Unknown Format: Skipping Crash"

		except:
			print 'Failed to get crash_id = ' + crash_id
			time.sleep(5)

		writer.close()
	reader.close()
	os.rename('october_crashes_5/' + files, 'october_crash_sets_parsed_5/' + files)