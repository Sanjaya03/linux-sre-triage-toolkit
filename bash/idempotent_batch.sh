#!/usr/bin/env bash
# =============================================================================
# Platform: Enterprise Sales & Incentive Compensation ($2B+ Volume, SOX ITGC)
# Subsystem: QIC Batch Operations & Filesystem Maintenance
# Description: Production-hardened runbook with atomic flock locking,
#              safe trap lifecycle, POSIX disk checks, and single-pass pruning.
# =============================================================================
set -euo pipefail

BASE_DIR="/tmp"
STAGING_DIR="${BASE_DIR}/qic_batch_staging"
LOCK_FILE="${BASE_DIR}/qic_maintenance.lock"
LOG_FILE="${BASE_DIR}/qic_maintenance.log"
RETENTION_DAY=7
THRESHOLD_PERCENTAGE=85
LOCK_ACQUIRED=0

log() {
    local level="$1"
    local message="$2"
    local timestamp
    timestamp="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

cleanup() {
    local exit_code="$?"
    if [[ "$LOCK_ACQUIRED" -eq 1 ]]; then
        rm -f "$LOCK_FILE"
    fi

    if [[ "$exit_code" -ne 0 ]]; then
        log "ERROR" "Script $0 has failed with error code ${exit_code}."
        exit "$exit_code"
    fi
    log "SUCCESS" "Script $0 completed successfully, Lock released."    
}

trap cleanup EXIT SIGTERM SIGINT

exec 200>"$LOCK_FILE"
if ! flock -n 200; then
    log "ERROR" "Another instance of $0 is already running. Exiting.."
    exit 1
fi
LOCK_ACQUIRED=1

log "INFO" "Starting QIC batch maintenance runbook..."

if [[ ! -d "$STAGING_DIR" ]]; then
    log "ERROR" "Staging directory $STAGING_DIR is missing in ${BASE_DIR}, Please check !"
    exit 1
fi

DISK_USAGE=$(df -P "$STAGING_DIR" | awk 'NR==2 {print $5}' | tr -d '%')
log "INFO" "Current disk utilization at ${DISK_USAGE}%."

if [[ "$DISK_USAGE" -gt "$THRESHOLD_PERCENTAGE" ]]; then
    log "WARNING" "$(df -P "$STAGING_DIR" | awk 'NR==2 {print $1}') is at ${DISK_USAGE}%, exceeding threshold !"
fi

PRUNE_COUNT=$(find "$STAGING_DIR" -type f -name "*.tmp" -mtime +"${RETENTION_DAY}" -print -delete | wc -l)

if [[ "$PRUNE_COUNT" -gt 0 ]]; then
    log "SUCCESS" "$PRUNE_COUNT number of files got deleted after exceeding retention period."
else
    log "INFO" "No .tmp file has exceeded retention period in $STAGING_DIR"
    log "SUCCESS" "QIC batch maintenance runbook completed successfully..."
fi
