import sys
import json
from pathlib import Path

LOG_FILE = '/home/sanjaya/sre/json_files/app_events.json.log'
if not Path(LOG_FILE):
    print(f"Log file {LOG_FILE} does not exist..")
    sys.exit(1)

error_count = 0
failling_api_endpoint = []

with open(LOG_FILE,'r') as log_line:
    for line in log_line:
        try:
            json_load = json.loads(line)
            status = json_load.get('status',0)
            if status >= 500:
                error_count += 1
                failling_api_endpoint.append(json_load.get('endpoint','unknown'))
        except json.JSONDecodeError:
            continue

print(f"No of 5XX error: {error_count} ")
print(f"Failing Endpoint: {failling_api_endpoint}")
sys.exit(0)
