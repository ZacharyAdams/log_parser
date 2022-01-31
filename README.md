# log_parser

This is a CLI program that reads an input file, e.g. access.log, containing new-line delimited entries in Common Log Format (https://en.wikipedia.org/wiki/Common_Log_Format). With the following functionality.

1. Read the log file, parse the entries, and output the data in JSON Lines (new-line delimited JSON) format

2. Aggregate the log entries, then print a summary of the data by request path. For each path, print the number of requests by status code class (2xx, 3xx, 4xx, …)

3. Search the input file for requests by request path and/or status code and print matching records.


How to use the Program

## Requirements
python3

### Useage

Run the python file by itself or with --help to see usage and examples.
```
./cli_log_parser.py --help
./cli_log_parser.py -s sample.log
./cli_log_parser.py -s sample.log -j
./cli_log_parser.py -s sample.log -j -d log.json
./cli_log_parser.py -s sample.log -a
./cli_log_parser.py -s sample.log -r /blogs
./cli_log_parser.py -s sample.log -c 200
./cli_log_parser.py -s sample.log -r /blogs -c 200
```
