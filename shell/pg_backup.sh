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

# Function to log messages
_log() {
    echo "$(date +"%b %d %H:%M:%S") $1" >&2
}

# Usage information
usage() {
    echo "Usage: $0 -h <host> -p <port> -u <username> -w <password> -d <output_directory> [-r <retention_days>]"
    echo "Environment variables can also be used: PGBACKUP_HOST, PGBACKUP_PORT, PGBACKUP_USERNAME, PGBACKUP_PASSWORD, PGBACKUP_DIR, PGBACKUP_RETENTION"
    exit 1
}

# Parse command line options
while getopts ":h:P:u:p:d:r:" opt; do
    case $opt in
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
_log "Starting backup to $BACKUP_FILE"
PGPASSWORD="$PASSWORD" pg_dumpall --clean -h "$HOST" -p "$PORT" -U "$USERNAME" > "$BACKUP_FILE"
# shellcheck disable=SC2181
if [[ $? -eq 0 ]]; then
    _log "Backup completed successfully"
else
    _log "Backup failed"
    exit 1
fi

# Cleanup old backups
_log "Cleaning up old backups"
while IFS= read -r file; do
    _log "Deleting $file"
    rm "$file"
done < <(find -L "$OUTPUT_DIR" -type f -name 'backup-*.sql' -mtime +"$RETENTION_DAYS" 2>/dev/null)

_log "Cleanup completed"

exit 0
