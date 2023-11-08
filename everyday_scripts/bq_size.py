#!/usr/bin/env python3
"""
This script displays the sizes and expiration times of tables in BigQuery for a given project. It allows users to
filter the results by datasets and tables using optional regex patterns. For day-partitioned tables, the partition
expiration duration in days is also displayed.

Usage:
    python bq_size.py PROJECT_ID [-d DATASET_REGEX] [-t TABLE_REGEX]

Arguments:
    PROJECT_ID: The GCP project ID.
    -d, --dataset: Regex pattern for datasets to include (optional).
    -t, --table: Regex pattern for tables to include (optional).
"""


from google.cloud import bigquery

# import sys
import argparse
from datetime import datetime, timezone
import re
from prettytable import PrettyTable
import warnings

warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")


def get_dataset_info(project_id: str, show_tables: bool = False) -> None:
    """
    Retrieves and prints information about BigQuery datasets and tables within the specified project.

    :param project_id: Google Cloud Project ID
    :param show_tables: Flag to show table-level information
    """
    client: bigquery.Client = bigquery.Client(project=project_id)
    never_expires_date = "9999-12-31"

    for dataset in client.list_datasets():
        dataset_ref: bigquery.DatasetReference = client.dataset(dataset.dataset_id)
        dataset_obj: bigquery.Dataset = client.get_dataset(dataset_ref)
        total_size_gb: float = 0
        table_details_list: list[tuple] = []
        for table_item in client.list_tables(dataset_obj):
            table: bigquery.Table = client.get_table(table_item)  # Fetch the full table object
            table_size_gb = table.num_bytes / (1024**3) if table.num_bytes else 0
            total_size_gb += table_size_gb
            if show_tables:
                if (not table.expires) or (table.expires.date().isoformat() == never_expires_date):
                    expiration_time = "Never Expires"
                else:
                    # Convert both datetimes to UTC before making them naive
                    table_expires_utc = table.expires.astimezone(timezone.utc).replace(tzinfo=None)
                    today_utc = datetime.now(timezone.utc).replace(tzinfo=None)
                    days_until_expiry = (table_expires_utc - today_utc).days
                    expiration_time = f"{table_expires_utc.date()} (in {days_until_expiry} days)"

                table_details = f"  - Table: {table.table_id}, Size: {table_size_gb:.2f} GB, Expiration Time: {expiration_time}"
                table_details_list.append((table_size_gb, table_details))

        default_expiration_time = dataset_obj.default_table_expiration_ms / 86400000 if dataset_obj.default_table_expiration_ms else "None"
        print(f"Dataset: {dataset.dataset_id}, Total Size: {total_size_gb:.2f} GB, Default Expiration Time: {default_expiration_time} days")

        # Sort table details by size in reverse order and print
        table_details_list.sort(reverse=True, key=lambda x: x[0])
        for _, table_detail in table_details_list:
            print(table_detail)


def main():
    parser = argparse.ArgumentParser(description="Display table sizes and expiration times in BigQuery.")
    parser.add_argument("project", help="GCP project ID.")
    parser.add_argument("-d", "--dataset", help="Regex pattern for datasets to include (optional).")
    parser.add_argument("-t", "--table", help="Regex pattern for tables to include (optional).")

    args = parser.parse_args()

    client = bigquery.Client(project=args.project)

    # List datasets in the project, optionally filtered by regex pattern
    datasets = list(client.list_datasets())
    for dataset in datasets:
        if args.dataset and not re.match(args.dataset, dataset.dataset_id):
            continue

        dataset_obj = client.get_dataset(dataset.dataset_id)
        handle_dataset(client, dataset_obj, args.table)


def handle_dataset(client: bigquery.Client, dataset: bigquery.Dataset, table_pattern: str | None = None):
    """
    Handles information retrieval and display for a given dataset in BigQuery. Lists tables within the dataset, their
    sizes, expiration times, and partition expiration durations if the tables are day partitioned. Filters tables
    based on an optional regex pattern.

    :param client: BigQuery client
    :param dataset: BigQuery Dataset object
    :param table_pattern: Regex pattern for tables to include (optional)
    """
    tables = []
    total_size_gb = 0

    # Retrieve the default table expiration for the dataset
    default_expiration_ms = dataset.default_table_expiration_ms
    default_expiration_str = f"{default_expiration_ms / 86400000} days" if default_expiration_ms else "None"

    for table_item in client.list_tables(dataset):
        table = client.get_table(table_item)
        size_gb = table.num_bytes / 1024 / 1024 / 1024 if table.num_bytes else 0
        total_size_gb += size_gb

        if table_pattern and not re.match(table_pattern, table_item.table_id):
            continue

        tables.append((table, size_gb))

    print(f"Dataset: {dataset.dataset_id}, Total Size: {total_size_gb:.2f} GB, Default Table Expiration: {default_expiration_str}\n")

    if not tables:
        print("No tables found in this dataset.\n")
        return

    # Create a pretty table
    table_display = PrettyTable()
    table_display.field_names = ["Table", "Size (GB)", "Expiration", "Partition Expiration"]
    table_display.align["Table"] = "r"  # Right align the table names

    # Sort tables by size in descending order
    tables.sort(key=lambda x: x[1], reverse=True)

    for table, size_gb in tables:
        expiration_str = "Never" if table.expires is None else table.expires
        partition_expiration_str = "None"

        # Check if the table is day partitioned and add partition expiration information
        if table.time_partitioning and table.time_partitioning.type_ == bigquery.TimePartitioningType.DAY:
            partition_expiration_ms = table.time_partitioning.expiration_ms
            partition_expiration_days = partition_expiration_ms / 86400000 if partition_expiration_ms else "Never"
            partition_expiration_str = f"{partition_expiration_days} days"

        table_display.add_row([table.table_id, f"{size_gb:.2f}", expiration_str, partition_expiration_str])

    print(table_display)
    print("\n" * 2)  # Two empty lines between datasets


if __name__ == "__main__":
    main()
