import os
import psycopg2
import sys

def get_stale_sessions():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST","127.0.0.1"),
            port = os.getenv("DB_PORT","5432"),
            dbname = os.getenv("DB_NAME","prod_app_db"),
            user = os.getenv("DB_USER","sre_app_user"),
            password = os.getenv("DB_PASSWORD","iamsre321")
        )

        cursor = conn.cursor()
        query = """select pid,state,now()-state_change time_taken, query from pg_stat_activity 
                where state = 'idle in transaction' and now()-state_change > interval '30 seconds';"""
        
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            print("[HEALTHY] No stale transaction found.")
        else:
            print(f"[ALERT] {len(rows)} transactions are stalled.")
            for pid,state,time_taken, query in rows:
                print(f"pid: {pid},state: {state},time_taken: {time_taken}, query: {query}")
        
        cursor.close()
        conn.close()
    
    except Exception as e:
        print(f"[ERROR] Failed : {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    get_stale_sessions()