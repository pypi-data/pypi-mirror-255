from cerebrium.core import cli  # noqa: E402 F401
from cerebrium.commands.storage import storage_app  # noqa: E402 F401
from cerebrium.commands.project import project_app

# from cerebrium.commands.utilities import delete_model, model_scaling  # noqa: E402 F401
from cerebrium.commands.app import app  # noqa: E402 F401
from cerebrium import __version__ as cerebrium_version
from cerebrium.commands.auth import login, save_auth_config  # Import the login function
from cerebrium.commands.cortex import init, deploy


cli.add_typer(storage_app, name="storage", help="Manage all storage operations")
cli.add_typer(
    app, name="app", help="See a list of your apps, their details and scale them"
)
cli.add_typer(
    project_app, name="project", help="Manage all functionality around your projects"
)


@cli.command()
def version():
    """
    Print the version of the Cerebrium CLI
    """
    print(cerebrium_version)


# Add commands directly to the CLI
cli.command()(login)
cli.command()(save_auth_config)
cli.command()(init)
cli.command()(deploy)


if __name__ == "__main__":
    cli()
