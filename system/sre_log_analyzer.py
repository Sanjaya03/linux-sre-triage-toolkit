#!/usr/bin/env python3

import argparse
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone

LOG_PATTERN = re.compile(r'"[A-Z]+\s+(\S+)\s+HTTP/[0-9.]+"\s+(5\d\d)')

def log(level,message):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = sys.stderr if level in ["ERROR","ABORTED"] else sys.stdout
    print(f"[{now}] [{level}] {message}", file=out)

def validate_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target log file:{file_path} does not exist.")
    if not os.path.isfile(file_path):
        raise ValueError(f"Path:{file_path} is not a regular file.")
    if not os.access(file_path,os.R_OK):
        raise PermissionError(f"Permission denied: Can not read {file_path}")

def stream_error_endpoints(file_path):
    with open(file_path,"r",encoding="utf-8",errors="replace") as f:
        for line in f:
            match = LOG_PATTERN.search(line)
            if match:
                endpoint = match.group(1)
                yield endpoint

def parse_arguments():
    parser = argparse.ArgumentParser(description="Enterprise Log Error Reporter")
    parser.add_argument("--file",required=True,type=str,help="Log file path")
    parser.add_argument("--top",type=int,default=2,help="Top 2 failing endpoints")

    return parser.parse_args()

def main():
    args = parse_arguments()

    try:
        log("INFO","Log Scanner Initiated..")

        validate_file(args.file)
        log("INFO",f"Scanning log file {args.file} for 5XX error.")

        error_count = Counter()
        
        for endpoint in stream_error_endpoints(args.file):
            error_count[endpoint] += 1

        total_err_count = sum(error_count.values())
        top_err_endpoints = error_count.most_common(args.top)

        log("INFO",f"Total number of 5XX error events: {total_err_count}")

        if top_err_endpoints:
            log("WARNING","5XX errors detected...")
            log("WARNING",f"Top {args.top} failed endpoints...")
            
            for rank,(endpoint,count) in enumerate(top_err_endpoints,start=1):
                log("WARNING",f"Rank: {rank} | No. of errors: {count} | Endpoint: {endpoint}")
                
            log("INFO","Log Scanner Completed..")
            sys.exit(1)
        else:
            log("INFO",f"No 5XX error captured in {args.file}")
            log("INFO","Log Scanner Completed..")
            sys.exit(0)

    except (FileNotFoundError,ValueError,PermissionError) as err:
        log("ERROR",f"Script failed, Error: {err}")
        sys.exit(1)
    except KeyboardInterrupt:
        log("ABORTED",f"{__file__} Execution cancelled by operator")
        sys.exit(130)

if __name__ == "__main__":
    main()
