import argparse
import logging
import subprocess
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )
log = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Production TLS Certificate Monitor Agent')
    parser.add_argument('--domain',default='google.com',help='Domain Name')
    parser.add_argument('--port',type=int,default=443,help='Port Number')
    args = parser.parse_args()

    log.info("............TLS Certification Expiry Monitor Agent Started............")
    log.info(f"......Initiating secure TLS check for {args.domain}:{args.port}......")

    try:
        p1 = subprocess.Popen(['openssl','s_client','-connect',f"{args.domain}:{args.port}",'-servername', args.domain],
                              stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        
        p2 = subprocess.Popen(['sed','-n','/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p'],
                             stdin=p1.stdout,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)

        cmd = subprocess.run(['openssl','x509','-noout','-enddate'],
                             stdin=p2.stdout,check=True,capture_output=True,text=True,timeout=5)
        
        cmd_output = cmd.stdout.strip()

        if "notAfter" in cmd_output:
            expiry_dt = cmd_output.replace("notAfter=","").strip()
            log.info(f"TLS certificate for {args.domain}:{args.port} expiring on {expiry_dt}")
            log.info("......................................................................")
            sys.exit(0)
        else:
            log.warning("TLS certification date extration failed")
            log.info("......................................................................")
            sys.exit(0)

    except subprocess.CalledProcessError as err:
        log.critical(f"TLS check shell command failed for {args.domain}:{args.port} Error: {err.stderr.strip()}")
        log.info("..........................................................................")
        sys.exit(1)
    except (subprocess.TimeoutExpired,FileNotFoundError) as err:
        log.warning(f"TLS check failed for {args.domain}:{args.port} Error: {err}")
        log.info("..........................................................................")
        sys.exit(1)

if __name__ == '__main__':
    main()