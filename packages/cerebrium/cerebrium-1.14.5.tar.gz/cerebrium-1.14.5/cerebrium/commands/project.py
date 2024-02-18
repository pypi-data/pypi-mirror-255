import typer
import os
import yaml
from typing import Optional
from typing_extensions import Annotated

import cerebrium.utils as utils
import cerebrium.logging as logging
from cerebrium.api import cerebrium_request, HttpMethod

project_app = typer.Typer()


@project_app.command("current")
def current():
    """
    Get the current project you are working in
    """
    print(f"projectId: {utils.get_current_project_context()}")


@project_app.command("list")
def list_projects():
    """
    List all your projects
    """
    projects_response = cerebrium_request(HttpMethod.GET, "projects", {})
    if projects_response is None:
        logging.cerebrium_log(
            level="ERROR",
            message="There was an error getting your projects. Please login again and, if the problem persists, contact support.",
            prefix="",
        )
        return

    if projects_response.status_code != 200:
        logging.cerebrium_log(
            level="ERROR",
            message="There was an error getting your projects",
            prefix="",
        )
        return

    if projects_response.status_code == 200:
        projects = projects_response.json()["projects"]
        for project in projects:
            print(f"{project['projectId']} : {project['name']}")
        print("")
        print(
            f"You can set your current project context by running 'cerebrium project set {projects[0]['projectId']}"
        )


@project_app.command("set")
def set_project(
    project_id: Annotated[
        str,
        typer.Argument(
            help="The projectId of the project you would like to work in",
        ),
    ],
):
    """
    Set the project context you are working in.
    """
    config_path = os.path.expanduser("~/.cerebrium/config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    config["project"] = project_id
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    print(f"Project context successfully set to : {project_id}")
