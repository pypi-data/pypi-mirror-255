import typer
import requests
from rich.panel import Panel
from rich import box
from rich.table import Table
from rich import print as console
from typing import Annotated, Optional

from cerebrium.api import cerebrium_request, HttpMethod
from cerebrium import logging

app = typer.Typer()


def _status_color(status: str) -> str:
    """Takes a status, returns a rich markup string with the correct color"""
    status = " ".join([s.capitalize() for s in status.split("_")])
    color = None
    if status == "Active":
        color = "green"
    elif status == "Cold":
        color = "bright_cyan"
    elif status == "Pending":
        color = "yellow"
    elif status == "Deploying":
        color = "bright_magenta"
    elif "error" in status.lower():
        color = "red"

    if color:
        return f"[bold {color}]{status}[bold /{color}]"
    else:
        return f"[bold]{status}[bold]"


def _pretty_timestamp(timestamp: str) -> str:
    """Converts a timestamp from 2023-11-13T20:57:12.640Z to human readable format"""
    return timestamp.replace("T", " ").replace("Z", "").split(".")[0]


@app.command("list")
def list():
    """
    List all apps under your current context
    """
    app_response = cerebrium_request(HttpMethod.GET, "get-models", {})
    if app_response.status_code != 200:
        logging.cerebrium_log(
            level="ERROR", message=f"There was an error getting your apps", prefix=""
        )
        return

    apps = app_response.json()

    apps_to_show = []
    for a in apps["models"]:
        # if isinstance(a, list):
        replicas = a.get("replicas", ["None"])
        replicas = [r for r in replicas if r != ""]
        # convert updatedat from 2023-11-13T20:57:12.640Z to human readable format
        updated_at = _pretty_timestamp(a.get("updatedAt", "None"))

        apps_to_show.append(
            {
                "id": f'{a["projectId"]}-{a["name"]}',
                "name": f'{a["name"]}',
                "status": _status_color(a["status"]),
                "replicas": replicas,
                "updatedAt": updated_at,
            }
        )

    # sort by updated date
    apps_to_show = sorted(apps_to_show, key=lambda k: k["updatedAt"], reverse=True)

    # Create the table
    table = Table(title="", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("ModelId")
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Replicas", justify="center")
    table.add_column("Last Updated", justify="center")

    for entry in apps_to_show:
        table.add_row(
            entry["id"],
            entry["name"],
            entry["status"],
            "\n".join(entry["replicas"]),
            entry["updatedAt"],
        )

    details = Panel.fit(
        table,
        title="[bold] App Details ",
        border_style="yellow bold",
        width=140,
        padding=(1, 1),
    )
    console(details)


@app.command("get")
def get(
    app_id: Annotated[
        str,
        typer.Argument(
            help="The app-id you would like to see the details",
        ),
    ]
):
    """
    Get specific details around a application
    """
    app_response = cerebrium_request(
        HttpMethod.GET, f"get-model-details?modelId={app_id}", {}
    )

    if app_response.status_code != 200:
        logging.cerebrium_log(
            level="ERROR",
            message=f"There was an error getting the details of app {app_id}.\n{app_response.json()['message']}",
            prefix="",
        )
        return

    app_response: dict = app_response.json()

    table = make_detail_table(app_response)
    details = Panel.fit(
        table,
        title=f"[bold] App Details for {app_id} [/bold]",
        border_style="yellow bold",
        width=100,
        padding=(1, 1),
    )
    print()
    console(details)
    print()


@app.command("delete")
def delete(
    name: Annotated[str, typer.Argument(..., help="Name of the Cortex deployment.")]
):
    """
    Delete a model or training job from Cerebrium
    """
    print(f'Deleting model "{name}" from Cerebrium...')
    delete_response = cerebrium_request(
        HttpMethod.DELETE, "delete-model", {"name": name}
    )
    if delete_response.status_code == 200:
        print("✅ Model deleted successfully.")
    else:
        print(f"❌ Model deletion failed.\n{delete_response.json()['message']}")


@app.command("scale")
def model_scaling(
    name: Annotated[str, typer.Argument(..., help="The name of your model.")],
    cooldown: Annotated[
        Optional[int],
        typer.Argument(
            ...,
            min=0,
            help=(
                "Update the cooldown period of your deployment. "
                "This is the number of seconds before your app is scaled down to 0."
            ),
        ),
    ] = None,
    min_replicas: Annotated[
        Optional[int],
        typer.Argument(
            ...,
            min=0,
            help=(
                "Update the minimum number of replicas to keep running for your deployment."
            ),
        ),
    ] = None,
    max_replicas: Annotated[
        Optional[int],
        typer.Argument(
            ...,
            min=1,
            help=(
                "Update the maximum number of replicas to keep running for your deployment."
            ),
        ),
    ] = None,
):
    """
    Change the cooldown, min and max replicas of your deployment via the CLI
    """
    if (
        max_replicas is not None
        and min_replicas is not None
        and max_replicas <= min_replicas
    ):
        logging.cerebrium_log(
            message="Maximum replicas must be greater than or equal to minimum replicas.",
            level="ERROR",
        )

    print(f"Updating scaling for model '{name}'...")
    if cooldown is not None:
        print(f"\tSetting cooldown to {cooldown} seconds...")
    if min_replicas is not None:
        print(f"\tSetting minimum replicas to {min_replicas}...")
    if max_replicas is not None:
        print(f"\tSetting maximum replicas to {max_replicas}...")

    body = {}
    if cooldown is not None:
        body["cooldownPeriodSeconds"] = cooldown
    if min_replicas is not None:
        body["minReplicaCount"] = min_replicas
    if max_replicas is not None:
        body["maxReplicaCount"] = max_replicas
    if not body:
        print("Nothing to update...")
        print("Cooldown, minReplicas and maxReplicas are all None ✅")

    body["name"] = name
    update_response = cerebrium_request(HttpMethod.POST, "update-model-scaling", body)
    if update_response.status_code == 200:
        print("✅ Model scaled successfully.")
    else:
        logging.cerebrium_log(
            level="ERROR",
            message=f"There was an error scaling {name}.\n{update_response.json()['message']}",
            prefix="",
        )


def make_detail_table(data: dict):
    def get(key):
        return str(data.get(key)) if data.get(key) else "Data Unavailable"

    def addRow(
        leader: str, key: str = "", value=None, ending: str = "", optional=False
    ):
        if value is None:
            if key not in data:
                ending = ""
            if optional:
                if data.get(key):
                    table.add_row(leader, get(key) + ending)
            else:
                table.add_row(leader, get(key) + ending)
        else:
            table.add_row(leader, str(value))

    # Create the tables
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column("Parameter", style="")
    table.add_column("Value", style="")
    table.add_row("MODEL", "", style="bold")
    table.add_row("Name", data.get("name"))
    addRow("Average Runtime", "averageModelRunTimeSeconds", ending="s")
    addRow("Cerebrium Version", "cerebriumVersion")
    addRow("Created At", "createdAt", _pretty_timestamp(get("createdAt")))
    if get("createdAt") != get("updatedAt"):
        addRow("Updated At", "updatedAt", _pretty_timestamp(get("updatedAt")))

    table.add_row("", "")
    table.add_row("HARDWARE", "", style="bold")
    table.add_row("GPU", get("hardware"))
    addRow("CPU", "cpu", ending=" cores")
    addRow("Memory", "memory", ending=" GB")
    if get("hardware") != "CPU" and "hardware" in data:
        addRow("GPU Count", "gpuCount")

    table.add_row("", "")
    table.add_row("SCALING PARAMETERS", "", style="bold")
    addRow("Cooldown Period", key="cooldownPeriodSeconds", ending="s")
    addRow("Minimum Replicas")
    if "maxReplicaCount" in data:
        addRow("Maximum Replicas", key="maxReplicaCount", optional=True)

    table.add_row("", "")
    table.add_row("STATUS", "", style="bold")
    addRow("Status", "status", value=_status_color(get("status")))
    addRow("Last Build Status", value=_status_color(get("lastBuildStatus")))
    addRow("Last Build Version", value=get("latestBuildVersion"), optional=True)

    if data.get("pods"):
        table.add_row("", "")
        table.add_row(
            "[bold]LIVE PODS[/bold]", "\n".join(data.get("pods", "Data Unavailable"))
        )

    return table
