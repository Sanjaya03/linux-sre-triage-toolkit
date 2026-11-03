import argparse
import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S %Z')
log = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Container cgroup Inspector')
    parser.add_argument('--container',type=str,default='pg_cgroup_labv2',help='Container Name')
    arg = parser.parse_args()

    log.info(f"---- Inspecting kernel cgroup limit for container {arg.container} -----")

    try:
        cmd = subprocess.run(['docker','exec',arg.container,'cat','/sys/fs/cgroup/memory.max'],
                            check=True,capture_output=True,text=True,timeout=5)
        cmd_output = cmd.stdout.strip()

        if cmd_output.isdigit():
            memory_limit = int(cmd_output) / (1024 * 1024)
            log.info(f"SUCCESS: Container {arg.container} cgroup memory limit is {memory_limit:.0f} Mb")
        else:
            log.info(f"SUCCESS: Container {arg.container} cgroup memory limit enforced as {cmd_output}")

        log.info("-----------------------------------------------------------------------")

    except (FileNotFoundError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as err:
        log.critical(f"FAILED: Container cgroup Inspector errored out with error: {err}")
        log.info("---------------------------------------------------------------------")
        sys.exit(1)

if __name__ == '__main__':
    main()