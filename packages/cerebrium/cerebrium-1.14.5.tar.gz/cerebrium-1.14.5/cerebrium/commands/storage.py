import json
import typer
from typing import Annotated, Optional

import cerebrium.logging as logging
from cerebrium.api import cerebrium_request, HttpMethod

storage_app = typer.Typer()


@storage_app.command("get-capacity")
def capacity():
    """A utility to view persistent storage capacity"""
    response = cerebrium_request(
        HttpMethod.GET,
        "get-storage-capacity",
    )
    if response.status_code == 200:
        storage = response.json()["capacity"]
        print(f"📦 Storage capacity: {storage} GB")
    else:
        logging.cerebrium_log(
            level="ERROR",
            message=f"There was an error getting your storage capacity.\n{response.json()['message']}",
            prefix="",
        )


@storage_app.command("increase-capacity")
def increase_capacity(
    increase: Annotated[
        int,
        typer.Argument(
            help="Increase storage capacity by the given number of GB. Warning: storage cannot be decreased once allocated and this will increase your monthly bill.",
            min=0,
        ),
    ] = 0,
):
    """A utility to increase persistent storage capacity."""
    if increase > 150:
        raise ValueError(
            "Increase value cannot be more than 150GB at a time. Otherwise, contact support if this is needed."
        )

    print(f"📦 Increasing storage capacity by {increase}GB...")
    response = cerebrium_request(
        HttpMethod.POST,
        "increase-storage-capacity",
        {"increaseInGB": increase},
    )
    if response.status_code == 200:
        new_size = response.json()["capacity"]
        print(f"✅ Storage capacity successfully increased to {new_size} GB.")
    else:
        logging.cerebrium_log(
            level="ERROR",
            message=f"There was an error updating your storage capacity.\n{response.json()['message']}",
            prefix="",
        )
