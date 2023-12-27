#!/bin/bash
#
# This script is used to perform backup of PostgreSQL database. It is intended to be used as a cronjob.
# Inputs can be given as environment variables.
#
set -e

# Default values
RETENTION_DAYS=7
PORT=5432
OUTPUT_DIR="/tmp"
DRY_RUN=0

# Function to log messages
_log() {
    echo "$(date +"%b %d %H:%M:%S") $1" >&2
}

# Usage information
usage() {
    echo "Usage: $0 [-n] -h <host> -p <port> -u <username> -w <password> -d <output_directory> [-r <retention_days>]"
    echo "Environment variables can also be used: PGBACKUP_HOST, PGBACKUP_PORT, PGBACKUP_USERNAME, PGBACKUP_PASSWORD, PGBACKUP_DIR, PGBACKUP_RETENTION"
    echo "-n: Dry run mode. No actual backup or deletion will be performed."
    exit 1
}

# Parse command line options
while getopts ":nh:P:u:p:d:r:" opt; do
    case $opt in
        n) DRY_RUN=1 ;;
        h) HOST=${OPTARG} ;;
        P) PORT=${OPTARG} ;;
        u) USERNAME=${OPTARG} ;;
        p) PASSWORD=${OPTARG} ;;
        d) OUTPUT_DIR=${OPTARG} ;;
        r) RETENTION_DAYS=${OPTARG} ;;
        *) usage ;;
    esac
done

# Override with environment variables if set
HOST=${PGBACKUP_HOST:-$HOST}
PORT=${PGBACKUP_PORT:-$PORT}
USERNAME=${PGBACKUP_USERNAME:-$USERNAME}
PASSWORD=${PGBACKUP_PASSWORD:-$PASSWORD}
OUTPUT_DIR=${PGBACKUP_DIR:-$OUTPUT_DIR}
RETENTION_DAYS=${PGBACKUP_RETENTION:-$RETENTION_DAYS}

# Check if required parameters are provided
if [[ -z "$HOST" || -z "$PORT" || -z "$USERNAME" || -z "$PASSWORD" || -z "$OUTPUT_DIR" ]]; then
    _log "Missing required parameters"
    usage
fi

# Perform backup
BACKUP_FILE="$OUTPUT_DIR/backup-$(date +%Y-%m-%d_%H-%M-%S).sql"

if [[ $DRY_RUN -eq 0 ]]; then
    _log "Starting backup to $BACKUP_FILE, and enforcing retention of $RETENTION_DAYS days in $OUTPUT_DIR"
    PGPASSWORD="$PASSWORD" pg_dumpall --clean -h "$HOST" -p "$PORT" -U "$USERNAME" > "$BACKUP_FILE"
    # shellcheck disable=SC2181
    if [[ $? -eq 0 ]]; then
        _log "Backup completed successfully"
    else
        _log "Backup failed"
        exit 1
    fi
else
    _log "DRYRUN: would have backed up to $BACKUP_FILE"
fi

# Cleanup old backups
_log "Starting cleanup of old backups"
current_date=$(date +%s)
retention_seconds=$((RETENTION_DAYS * 24 * 60 * 60))

find -L "$OUTPUT_DIR" -type f -name 'backup-*.sql' -print0 2>/dev/null | while IFS= read -r -d $'\0' file; do
    filename=$(basename "$file")
    backup_date_str=$(echo "$filename" | perl -pe 's/backup-(\d+)-(\d+)-(\d+)_(\d+)-(\d+)-(\d+).sql/$1-$2-$3 $4:$5:$6/')

    if [[ "$OSTYPE" == "darwin"* ]]; then
        backup_date=$(date -j -f "%Y-%m-%d %H:%M:%S" "$backup_date_str" +%s)
    else
        backup_date=$(date -d "$backup_date_str" +%s)
    fi
    # echo "Backup date of $file: $backup_date_str -> $backup_date epoch"
    if (( current_date - backup_date > retention_seconds )); then
        age_str="(age=$((( current_date - backup_date) / 86400)) days)"
        if [[ $DRY_RUN -eq 0 ]]; then
            _log "Deleting $file $age_str"
            rm "$file"
        else
            _log "DRYRUN: would delete $file $age_str"
        fi
    fi
done

_log "Cleanup completed"
exit 0
