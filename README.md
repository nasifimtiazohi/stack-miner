# stack-miner
These scripts are designed to help researchers acquire crash dump stack traces for security research purposes.

## Dependencies

These scripts are written in Python 3. They require Selenium and termcolor to run.

## miner.py

```
usage: miner.py [-h] [-b {firefox}] [--start START] [--stop STOP]
                {fedora} url output

Invokes parser.py to grab stack traces from the specified source.

positional arguments:
  {fedora}                The indexing service from which the results are to be
                          parsed.
  url                     The URL of the search results. Use {} as the
                          placeholder for page number.
  output                  Path to the file to which the parse results should be
                          written.

optional arguments:
  -h, --help            Show this help message and exit
  -b {firefox}          The browser to use when retrieving the search results.
  --start START         Index of the page of results to start parsing from.
  --stop STOP           Index of the page of results to stop parsing to.
```
Example that scrapes the first two pages:

```
python miner.py -b firefox fedora https://retrace.fedoraproject.org/faf/reports/?order_by=count&associate=__None&first_occurrence_daterange=&component_names=&last_occurrence_daterange=2017-05-22%3A2017-06-20&offset={} test.csv --start 0 --stop 40
```

The firefox folder needs to be integrated with the current set of scripts. Currently has some hard coded badness I need to refactor...

### TODOs

* Remove hard coded figures and pass parameters for source/dest files and the API URL
* Merge with the scripts used for Fedora

### crash_id_grabber.py

Grabs crash ID's for the specified time period. Recommend 200 crash ID's per pull to be a good neighbor.

### crash_info_grabber.py

Takes output from crash_id_grabber.py and pulls all crash ID's from specified directory.

### clean_firefox_metrics.py

Cleans up the software engineering metrics from Understand.

### get_churn_stats.py

Takes a list of source code files with relative paths and gets churn data.

### get_vuln_data.py

Checks an external list of vulnerable files against the files found in the metric sheet to make sure no files are missing/spelled incorrectly in either list.

### Current workflow:

```

crash_id_grabber.py -> crash_info_grabber.py -> crash data

Understand Data
      |
      V
clean_firefox_metrics.py > get_churn_stats.py > get_vuln_data.py
```
