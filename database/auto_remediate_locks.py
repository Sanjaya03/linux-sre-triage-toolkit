import argparse
import psycopg2
import os
import sys
import json
import datetime

def remidate_stale_sessions(execute=False,threshold_seconds=30):
    threshold_interval = datetime.timedelta(seconds=threshold_seconds)
    query = """
            select pid,usename,now()-state_change duration,query from pg_stat_activity
            where usename != 'postgres' and state = 'idle in transaction' and now()-state_change > %s
            
            """
    try:
        with psycopg2.connect( 
            host = os.getenv("DB_HOST","127.0.0.1"),
            port = os.getenv("DB_PORT","5432"),
            dbname = os.getenv("DB_NAME","prod_app_db"),
            user = os.getenv("DB_USER","sre_app_user"),
            password = os.getenv("DB_PASSWORD","iamsre321")
        ) as conn:
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(query,(threshold_interval,))
                rows = cursor.fetchall()

                if not rows:
                    print(json.dumps({"status": "Healthy","message": "no stale transaction found."}))
                    return
                
                for pid,usename,duration,query in rows:
                    if not execute:
                        print(json.dumps({
                            "action": "[DRY RUN]",
                            "message": f"would terminate stale transaction {pid}",
                            "user": usename,
                            "idle_seconds": duration.total_seconds()
                            }))
                    else:
                        cursor.execute("select pg_terminate_backend(%s)",(pid,))
                        print(json.dumps({
                            "action": "terminated",
                            "pid": pid,
                            "user": usename
                        }))
    
    except Exception as e:
        print(json.dumps({
            "Status": "Failed",
            "message": f"remidiation script failed:{e}"
        }))            
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PostgreSQL SRE Auto-Remediation Daemon")
    parser.add_argument("--execute",action="store_true",help="terminate session indicator")
    parser.add_argument("--seconds",type=int,default=30,help="threshold seconds")
    args = parser.parse_args()

    remidate_stale_sessions(execute=args.execute,threshold_seconds=args.seconds)