#!/usr/bin/env python3

import google.cloud.bigquery as bigquery

from google.api_core.exceptions import NotFound

import argparse

import sys
import re
import warnings

warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")


def set_partition_expiration(client: bigquery.Client, table: bigquery.Table, days: int, dry_run: bool) -> None:
    """
    Sets the partition expiration for a given day-partitioned table and prints the change.
    If days is set to -1, the partition expiration will be removed.

    :param client: BigQuery client
    :param table: Table object
    :param days: Number of days for partition expiration, or -1 to remove expiration
    :param dry_run: Flag for dry run
    """

    before_expiration_ms = table.time_partitioning.expiration_ms  # type: ignore
    before_expiration_days = before_expiration_ms / 86400000 if before_expiration_ms else "None"
    after_expiration_days = None if days == -1 else days

    print_line = f"Table: {table.table_id}, Partition Expiration Time: {before_expiration_days} days -> {after_expiration_days} days"
    dry_run_suffix = " [DRYRUN]" if dry_run else ""
    print(f"{print_line}{dry_run_suffix}")

    if not dry_run:
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY, expiration_ms=None if days == -1 else days * 86400000
        )
        client.update_table(table, ["time_partitioning"])


def handle_tables(
    client: bigquery.Client,
    dataset_obj: bigquery.Dataset,
    days: int,
    table_pattern: str | None = None,
    skip_tables: str | None = None,
    dry_run: bool = False,
) -> None:
    """
    Handles the partition expiration time for tables within the specified dataset. Only day-partitioned tables are affected.

    :param client: BigQuery Client
    :param dataset_obj: BigQuery Dataset object
    :param days: Number of days for partition expiration, or -1 to remove expiration
    :param table_pattern: Regex pattern for tables to set expiration (optional)
    :param skip_tables: Regex pattern to skip tables that should not be affected (optional)
    :param dry_run: Flag for dry run, show changes without applying them
    """

    for table_item in client.list_tables(dataset_obj):
        table: bigquery.Table = client.get_table(table_item)  # Fetch the full table object

        # Skip tables that match the skip_tables regex pattern if provided
        if skip_tables and re.match(skip_tables, table.table_id):
            continue

        # If a table_pattern is provided, skip tables that don't match the regex pattern
        if table_pattern and not re.match(table_pattern, table.table_id):
            continue

        # Check if the table is day-partitioned
        if table.time_partitioning and table.time_partitioning.type_ == bigquery.TimePartitioningType.DAY:
            set_partition_expiration(client, table, days, dry_run)


def main():
    parser = argparse.ArgumentParser(description="Change partition expiration for day-partitioned tables in BigQuery.")
    parser.add_argument("project", help="GCP project ID.")
    parser.add_argument("dataset", help="BigQuery dataset ID.")
    parser.add_argument(
        "-d", "--days", type=int, required=True, help="Number of days for partition expiration, or -1 to remove expiration."
    )
    parser.add_argument("-t", "--table", help="Regex pattern for tables to set expiration (optional).")
    parser.add_argument("-s", "--skip-tables", help="Regex pattern to skip tables that should not be affected (optional).")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Dry run, show changes without applying them.")

    args = parser.parse_args()

    try:
        # Initialize BigQuery client
        client = bigquery.Client(project=args.project)

        # Get the dataset object
        dataset_id = f"{args.project}.{args.dataset}"
        dataset_obj = client.get_dataset(dataset_id)

        # Handle the partition expiration for tables
        handle_tables(client, dataset_obj, args.days, args.table, args.skip_tables, args.dry_run)

    except KeyboardInterrupt:
        print("\nOperation canceled by user. Exiting.")
        sys.exit(0)

    except NotFound as e:
        print(f"Dataset not found: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
