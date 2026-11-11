#!/usr/bin/env python3

import argparse
import os
import sys
from datetime import datetime, timezone


def log(level,message):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{now}] [{level}] {message}")

def get_load_average():
    with open("/proc/loadavg","r") as f:
        parts = f.read().split()
        return float(parts[0]), float(parts[1]), float(parts[2]), parts[3]

def get_memory_metrics():
    mem_data = {}
    with open("/proc/meminfo","r") as f:
        for line in f:
            if line.startswith(("MemTotal:", "MemAvailable:")):
                parts = line.split(":")
                mem_data[parts[0]] = int(parts[1].split()[0])
    total_mb = round(mem_data.get("MemTotal",1)/1024,2)
    avail_mb = round(mem_data.get("MemAvailable",1)/1024,2)
    used_pct = round(((total_mb - avail_mb)/total_mb)*100,2)

    return total_mb,avail_mb,used_pct

def scan_process_states():
    count = {"R": 0,"S": 0,"D": 0,"Z": 0}
    problem_process = []

    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            with open(f"/proc/{pid}/stat","r") as f:
                content = f.read()
                name = content[content.find("(") + 1 : content.rfind(")")]
                state = content[content.rfind(")") + 2]

                if state in count:
                    count[state] += 1
                if state in ["D","Z"]:
                    problem_process.append((pid,name,state))
        except (FileNotFoundError,PermissionError,ProcessLookupError):
            continue

    return count, problem_process

def parse_arguments():
    parser = argparse.ArgumentParser(description="Enterprise SRE Linux /proc Diagnostic CLI")
    parser.add_argument("--load-threshold",type=float,default=4.0,help="1m load average threshold (default: 4.0)")
    parser.add_argument("--mem-threshold",type=float,default=85.0,help="Memory used percentage threshold (default: 85.0)")

    return parser.parse_args()

def main():
    args = parse_arguments()
    
    log("INFO", "Enterprise logger initialized.")
    degradation = False
    
    load1, load5, load15, threads = get_load_average()
    log("INFO",f"CPU load 1m: {load1} | 5m: {load5} | 15m: {load15} | Threads: {threads}")
    if load1 > args.load_threshold:
        log("WARNING",f"Load average has execeeded threshold {args.load_threshold}")
        degradation = True
    
    total_mb,avail_mb,used_pct = get_memory_metrics()
    log("INFO",f"Memory Total: {total_mb}Mb | Available Memory: {avail_mb}Mb | Used Percentage: {used_pct}%")
    if used_pct >= args.mem_threshold:
        log("WARNING",f"Available RAM {used_pct}% has been execeeded threshold {args.mem_threshold}")
        degradation = True

    count, problem_process = scan_process_states()
    log("INFO",f"Process States: Running(R): {count["R"]} | Sleeping(S): {count["S"]} | DiskWait(D): {count["D"]} | Zombie(Z): {count["Z"]}")
    if problem_process:
        for pid,name,state in problem_process:
            desc = "DISK I/O Freeze" if state == "D" else "Zombie"
            log("CRITICAL",f"Problem Process Details: PID: {pid} | Name: {name} | State: {state} | Desc: {desc}")
        degradation = True

    if degradation:
        log("ERROR","System degradation detected. Exiting with code 1.")
        sys.exit(1)
    
    log("SUCCESS","Enterprise logger completed. System is healthy.")
    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("ERROR","Execution interrupted by user. Exiting cleanly.")
        sys.exit(130)
