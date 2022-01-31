#!/usr/bin/env python3
import argparse
import json
import sys
import os

def getArgs():
    p = argparse.ArgumentParser()
    p.add_argument("-s", "--source", required=True, help="The source log file you wish to use the cli tool on (./cli_log_parser.py -s sample.log)")
    p.add_argument("-j", "--json", help="Option to create a json file from the CLF log file provided with source (./cli_log_parser.py -s sample.log -j)", action="store_true")
    p.add_argument("-d", "--destination", help="Destination you wish to save the converted CLF log file to in JSON format (./cli_log_parser.py -s sample.log -j -d log.json)")
    p.add_argument("-a", "--aggregate", help="Agreegate the status codes by status classes 2XX, 3XX, 4XX, 5XX (./cli_log_parser.py -s sample.log -a)", action="store_true")
    p.add_argument("-r", "--request", help="Filter option when using -r, for filtering by request path (./cli_log_parser.py -s sample.log -r /blogs)")
    p.add_argument("-c", "--status", help="Filter option when using -c, for filtering by status code ./cli_log_parser.py -s sample.log -c 200")
    return p.parse_args()

def convertLogToDict(log):
    """With log path (if exists) or log,string
    return list of dictionaries"""

    log_string = None
    if os.path.exists(log):
        with open(log, 'r') as f:
            log_string = f.read()
    else:
        log_string = log
    
    log_headers = {
        'host': 0,
        'ident': 1,
        'authuser': 2,
        'date_a': 3,
        'date_b': 4,
        'method': 5,
        'requestpath': 6,
        'protocol': 7,
        'status': 8,
        'bytes': 9,
        'client': 10
    }
    
    log_obj = []
    log_lines = log_string.split('\n')
    for line in log_lines:
        line_parts = line.split()
        if len(line_parts) < 11:
            continue
        line_dict = {}

        host_string = line_parts[log_headers['host']]
        ident_string = line_parts[log_headers['ident']]
        authuser_string = line_parts[log_headers['authuser']]
        status_string = line_parts[log_headers['status']]
        bytes_string = line_parts[log_headers['bytes']]
        client_string = line_parts[log_headers['client']]

        date_string = ' '.join(line_parts[
            log_headers['date_a']:log_headers['date_b']+1
        ])
        request_string = ' '.join(line_parts[
            log_headers['method']:log_headers['protocol']+1
            ])

        line_dict.update({
            'host': host_string,
            'ident': ident_string,
            'authuser': authuser_string,
            'date': date_string,
            'request': request_string,
            'status': status_string,
            'bytes': bytes_string,
            'client': client_string
        })

        log_obj.append(line_dict)

    return log_obj

def save_as_json(content, destination=None):
    with open(destination, 'w') as f:
        f.write(content)
    return

def get_request_counts(log_dict):
    """With log as list of dicts
    show unique request paths with a count of their status codes

    Remove status code classes if we want to just report all status codes
    """
    random_unique_status = set()
    for line in log_dict:
        status_code_classes = line["status"][0] + "XX's"
        random_unique_status.add(status_code_classes)
    unique_status = list(random_unique_status)
    unique_status.sort()

    req_path_counts = {}
    for line in log_dict:
        status_code_classes = line["status"][0] + "XX's"
        req_type, req_path, req_protocol = line['request'].split()
        if req_path not in req_path_counts:
            req_path_counts[req_path] = {}
            for status_code_classes in unique_status:
                req_path_counts[req_path].update({status_code_classes: 0})

        req_path_counts[req_path][status_code_classes] += 1

    return req_path_counts

def query_logs(log, query, by):
    """Get log lines matching path or status"""

    # Just load the file (with open)

    with open(log, 'r') as f:
        log_content = f.read()

    log_headers = {
        'host': 0,
        'ident': 1,
        'authuser': 2,
        'date_a': 3,
        'date_b': 4,
        'method': 5,
        'requestpath': 6,
        'protocol': 7,
        'status': 8,
        'bytes': 9,
        'client': 10
    }

    matching_lines = []
    log_lines = log_content.split('\n')
    for line in log_lines:
        line_parts = line.split()
        if len(line_parts) < 11:
            continue
        status_string = line_parts[log_headers['status']]
        request_string = ' '.join(line_parts[
            log_headers['method']:log_headers['protocol']+1
            ])

        if by == "status" and query == status_string:
            matching_lines.append(line)

            """Sure! Using .split() without arguments chops up that piece by spaces. 
            If I recall it returned something like ['GET', '/blog/abc', 'HTTP/1.1']  
            If I wrote-- a, request_path, c = request_string.split() -- 
            then a and c would be variables for the first and third piece ("GET" and "HTTP/1.1").  
            Instead of a variable name I used underscores to kind of discard the unused results. 
            I saw a video one time where someone did that in a loop and finally had a reason to use it!"""

        _, request_path, _ = request_string.split()
        if by == "request" and query == request_path:
            matching_lines.append(line)

    return matching_lines

def main(args):
    search_results = None
    search_request = False
    search_status = False
    log_data = convertLogToDict(args.source)

    if args.json:
        json_string = json.dumps(log_data, indent=4)
        if not args.destination:
            print(json_string)
        else:
            save_as_json(json_string, args.destination)
    
    if args.aggregate:
        req_path_counts = get_request_counts(log_data)
        for req_path, status_counts in req_path_counts.items():
            print()
            print(f"Request path: '{req_path}'")
            for status, count in status_counts.items():
                print(f'Status: {status} ({count})')

    if args.status:
        status_results = query_logs(args.source, args.status, by="status")
        search_status = True
    if args.request:
        request_results = query_logs(args.source, args.request, by="request")
        search_request = True
    if search_status and search_request:
        search_results = [line for line in request_results if line in status_results]
        print('\n'.join(search_results))
    elif search_status and not search_request:
        print('\n'.join(status_results))
    elif not search_status and search_request:
        print('\n'.join(request_results))    


if __name__ == '__main__':
    main(getArgs())