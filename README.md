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
