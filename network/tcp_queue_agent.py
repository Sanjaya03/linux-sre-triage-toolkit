import argparse
import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Production TCP Queue & Reset Risk Agent')
    parser.add_argument('--port',default=5432,type=int,help='Port number')
    arg = parser.parse_args()

    log.info("----------------------------Production TCP Queue & Reset Risk Agent Report------------------")

    try:
        cmd = subprocess.run(['ss','-lnt'], check=True, capture_output=True, text=True, timeout=5)
        cmd_output = cmd.stdout.splitlines()

        target_line = [line for line in cmd_output if f":{arg.port}" in line]

        if not target_line:
           log.warning(f"No active listening TCP socket found on port {arg.port}!")
           log.info("---------------------------------------------------------------------------------------------")
           sys.exit(1)

        max_pct = 0

        for port in target_line:
            col_output = port.split()
            Recv_Q = int(col_output[1])
            Send_Q = int(col_output[2])

            if Send_Q > 0:
                usg_perct = int((Recv_Q / Send_Q) * 100)
                max_pct = usg_perct

        if max_pct > 80:
            log.critical(f"Listen queue on port {arg.port} is >= 80% full! Risk of RST drops!")
        else:
            log.info(f"SUCCESS: Socket port {arg.port} is HEALTHY (Queue Saturation: {max_pct}%).")

        log.info("---------------------------------------------------------------------------------------------")

    except FileNotFoundError as err:
        log.warning(f"System binary missing ! Error: {err}")
        sys.exit(1)
    except subprocess.CalledProcessError as err:
        log.critical(f"Shell command failed, please check command. System Error: {err.stderr.strip()}")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        log.warning("timeout has occured while executing shell command")
        sys.exit(1)

if __name__ == '__main__':
    main()