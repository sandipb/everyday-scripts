#!/usr/bin/env python3
import re
import click
from google.cloud import monitoring_v3
import google.api.metric_pb2 as metric_pb2


def value_type_string(value_type: metric_pb2.MetricDescriptor.ValueType) -> str:  # type: ignore
    """Convert metric_pb2.MetricDescriptor.ValueType to string."""
    return metric_pb2.MetricDescriptor.ValueType.Name(value_type)  # type: ignore


def kind_string(kind: metric_pb2.MetricDescriptor.MetricKind) -> str:  # type: ignore
    """Convert metric_pb2.MetricDescriptor.MetricKind to string."""
    return metric_pb2.MetricDescriptor.MetricKind.Name(kind)  # type: ignore


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("--project-id", required=True, help="The ID of the Google Cloud project to use.")
@click.pass_context
def cli(ctx, project_id):
    ctx.obj = {"project_id": project_id}


@click.command()
@click.option("--pattern", "-p", default="", help="Regex pattern to filter metric types.")
@click.pass_context
def list(ctx, pattern: str):
    """List custom GCP metrics for a project."""
    project_id = ctx.obj["project_id"]
    project_name = f"projects/{project_id}"
    client = monitoring_v3.MetricServiceClient()

    # List all metric descriptors for the project
    metrics = client.list_metric_descriptors(name=project_name)

    # Compile regex pattern if provided
    regex = re.compile(pattern) if pattern else None
    for metric in metrics:
        metric_type: str = metric.type  # type: ignore
        # Filter out non-custom metrics
        if not metric_type.startswith("custom.googleapis.com/"):
            continue

        # remove prefix
        metric_type = metric_type[len("custom.googleapis.com/") :]

        # Apply regex filter if provided
        if regex and not regex.search(metric_type):  # type: ignore
            continue

        desc = {
            "name": metric_type,
            "description": metric.description,  # type: ignore
            "unit": metric.unit,  # type: ignore
            "labels": ",".join([lbl.key for lbl in metric.labels]),  # type: ignore
            "kind": kind_string(metric.metric_kind),  # type: ignore
            "type": value_type_string(metric.value_type),  # type: ignore
        }

        key_color = "blue"
        value_color = "green"

        metric_str = f"{desc['name']}\t"

        for key, value in desc.items():
            if key == "name":
                continue
            metric_str += f"{click.style(key, fg=key_color)}={click.style(value, fg=value_color)} "
        print(metric_str)


@click.command()
@click.argument("metric_name", type=str)
@click.pass_context
def delete(ctx, metric_name: str):
    """Delete a custom GCP metric."""
    project_id = ctx.obj["project_id"]
    project_name = f"projects/{project_id}"

    # Initialize the MetricServiceClient
    client = monitoring_v3.MetricServiceClient()

    request = monitoring_v3.ListMetricDescriptorsRequest(name=project_name, filter=f'metric.type = "custom.googleapis.com/{metric_name}"')

    metric_descriptors = client.list_metric_descriptors(request=request)

    metric_descriptor = next(iter(metric_descriptors), None)
    if metric_descriptor is None:
        click.echo(f"Metric {metric_name} not found.")
        return

    if click.confirm(f'Do you want to delete "{metric_descriptor.type}" ?'):  # type: ignore
        client.delete_metric_descriptor(name=metric_descriptor.name)  # type: ignore
        click.echo(f"Deleted metric {metric_name}.")


def main():
    cli.add_command(list)
    cli.add_command(delete)
    cli()


if __name__ == "__main__":
    main()
