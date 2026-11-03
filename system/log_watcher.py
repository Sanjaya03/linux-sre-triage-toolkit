import json
import os
import re
import sys

import requests

LOG_FILE = "/home/sanjaya/sre/logs/payment_app.log"
CONFIG_FILE = "/home/sanjaya/sre/config/alerts.json"

if not os.path.isfile(LOG_FILE):
    print(f"ERROR: File {LOG_FILE} does not exist", file=sys.stderr)
    sys.exit(1)

pattern = r'ERROR: '

with open(LOG_FILE, 'r') as log_line:
    for line in log_line:
        match = re.search(pattern, line, re.IGNORECASE)
        if not match:
               print(f"INFO: No error found in the log line: {line.strip()}")
               sys.exit(1)

try:
    with open(CONFIG_FILE, 'r') as config_line:
        config = json.load(config_line)
        webhook_url = config.get("webhook_url")
        response = requests.post(webhook_url, json=webhook_url, timeout=5)
        response.raise_for_status()
except FileNotFoundError:
                print(f"ERROR: Configuration file {CONFIG_FILE} not found", file=sys.stderr)
                sys.exit(1)
except json.JSONDecodeError as error:
                print(f"ERROR: Failed to read alert configuration: {error}", file=sys.stderr)
                sys.exit(1)

print("Log watcher script completed successfully.")