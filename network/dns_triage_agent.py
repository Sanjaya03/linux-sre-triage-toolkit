import argparse
import logging
import socket
import subprocess
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

log = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Production DNS and DB Resloution Agent')
    parser.add_argument('--hostname', default='localhost', help='Target hostname')
    parser.add_argument('--port', type=int, default=5432, help='Target port')
    arg = parser.parse_args()

    log.info(f"DNS resolution for {arg.hostname} has started")

    try:
        ip_resolve = socket.gethostbyname(arg.hostname)
        log.info(f"IP address of {arg.hostname}: {ip_resolve}")
        log.info(f"DNS resolution for {arg.hostname} has completed")

    except socket.gaierror as err:
        log.critical(f"DNS resolution for {arg.hostname} failed with Error: {err}")
        sys.exit(1)

    log.info(f"DB availability check for {arg.hostname} Started")

    try:
        db_check_cmd = subprocess.run(
            ["pg_isready", "-h",ip_resolve,"-p",str(arg.port)],
            check=True,
            capture_output=True,
            text=True,
            timeout=5
            )
        result = db_check_cmd.stdout.strip()
        log.info(f"{result}")
        log.info(f"DB availability check for {arg.hostname} Ended")
        sys.exit(0)

    except FileNotFoundError as err:
        log.critical(f"DB availability failed..ERROR: {err}")
        sys.exit(1)
    except subprocess.CalledProcessError as err:
        log.critical(f"DB availability failed..ERROR: {err.stderr.strip()}")
        sys.exit(1)
    except subprocess.TimeoutExpired as err:
        log.warning(f"DB availability failed check for {arg.hostname} and {arg.port} Timeout Exiting..{err}")

if __name__ == '__main__':
    main()  