#!/usr/bin/env python3

from google.cloud import bigquery
from google.api_core.exceptions import NotFound
import argparse
from datetime import timedelta, datetime, timezone
import sys
import re
import warnings
from typing import Union

warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")


def set_expiration(
    client: bigquery.Client, item: Union[bigquery.Dataset, bigquery.Table], days: int, dry_run: bool, table_name: str | None = None
) -> None:
    """
    Sets the expiration for a given item (dataset or table) and prints the change.
    If days is set to -1, the expiration will be removed.

    :param client: BigQuery client
    :param item: Dataset or table object
    :param days: Number of days for expiration, or -1 to remove expiration
    :param dry_run: Flag for dry run
    :param table_name: Name of the table (if applicable)
    """
    if isinstance(item, bigquery.Dataset):
        before_expiration_ms = item.default_table_expiration_ms
        before_expiration_days = before_expiration_ms / 86400000 if before_expiration_ms else "None"
        after_expiration_days = None if days == -1 else days
        print_line = f"{item.dataset_id}: Expiration Time: {before_expiration_days} days -> {after_expiration_days} days"
    else:
        before_expiration = item.expires
        before_expiration_str = (
            f"{before_expiration.astimezone(timezone.utc).isoformat()} ({(before_expiration - datetime.utcnow().replace(tzinfo=timezone.utc)).days} days)"
            if before_expiration
            else "None"
        )

        after_expiration_time = None if days == -1 else datetime.utcnow() + timedelta(days=days)
        after_expiration_str = (
            f"{after_expiration_time.astimezone(timezone.utc).isoformat()} ({days} days)" if after_expiration_time else "None"
        )
        print_line = f"Table: {table_name}, Expiration Time: {before_expiration_str} -> {after_expiration_str}"

    dry_run_suffix = " [DRYRUN]" if dry_run else ""
    print(f"{print_line}{dry_run_suffix}")

    if not dry_run:
        if isinstance(item, bigquery.Dataset):
            item.default_table_expiration_ms = None if days == -1 else days * 86400000
            client.update_dataset(item, ["default_table_expiration_ms"])
        else:
            item.expires = None if days == -1 else datetime.utcnow() + timedelta(days=days)
            client.update_table(item, ["expires"])


def handle_tables(
    client: bigquery.Client,
    dataset_obj: bigquery.Dataset,
    days: int,
    table_pattern: str | None = None,
    skip_tables: str | None = None,
    dry_run: bool = False,
) -> None:
    """
    Handles the expiration time for tables within the specified dataset.

    :param client: BigQuery Client
    :param dataset_obj: BigQuery Dataset object
    :param days: Number of days for expiration
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

        # Call set_expiration function to handle expiration for the table
        set_expiration(client, table, days, dry_run, table_name=table.table_id)


def main() -> None:
    """
    Main function to parse command-line arguments and handle expiration changes.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Set default expiration for BigQuery datasets and optionally tables within a specified Google Cloud Project."
    )
    parser.add_argument("project_id", help="Google Cloud Project ID")
    parser.add_argument("dataset_name", help="BigQuery Dataset Name")
    parser.add_argument("-d", "--days", type=int, required=True, help="Number of days for expiration")

    # Create a mutually exclusive group for --all-tables and --table
    table_group = parser.add_mutually_exclusive_group()
    table_group.add_argument("-a", "--all-tables", action="store_true", help="Set expiration for all tables")
    table_group.add_argument("-t", "--table", type=str, help="Regex pattern for tables to set expiration")

    parser.add_argument("-s", "--skip-tables", type=str, help="Regex pattern to skip tables that should not be affected")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Dry run, show changes without applying them")
    args: argparse.Namespace = parser.parse_args()

    try:
        client: bigquery.Client = bigquery.Client(project=args.project_id)
        dataset_id = f"{args.project_id}.{args.dataset_name}"
        dataset_obj: bigquery.Dataset = client.get_dataset(dataset_id)  # Fetch dataset directly

        # Only change the dataset's default expiration if neither --all-tables nor --table is provided
        if not (args.all_tables or args.table):
            set_expiration(client, dataset_obj, args.days, args.dry_run)

        if args.all_tables or args.table:
            handle_tables(client, dataset_obj, args.days, args.table, args.skip_tables, args.dry_run)

    except KeyboardInterrupt:
        print("\nOperation canceled by user. Exiting...")
        sys.exit(0)
    except NotFound as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
