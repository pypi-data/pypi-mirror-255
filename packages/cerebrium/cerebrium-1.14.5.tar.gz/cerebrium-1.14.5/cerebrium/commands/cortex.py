import os
import shutil
import tempfile
import typer
import yaml
from termcolor import colored
from rich.console import Group
from rich.panel import Panel
from rich import print as console
from typing_extensions import Annotated, Optional
import time
import threading
import inspect
import sys

from rich.live import Live
from rich.text import Text
from rich.spinner import Spinner
from cerebrium import datatypes


import cerebrium.api as api
from cerebrium.api import cerebrium_request, HttpMethod
import cerebrium.sync_files as sync_files
from cerebrium import utils
from cerebrium import logging
from cerebrium.core import cli
from cerebrium.datatypes import *
from cerebrium import verification
from cerebrium import __version__ as cerebrium_version
from cerebrium.sync_files import (
    upload_files_to_s3,
    upload_marker_file_and_delete,
)
from cerebrium.logging import cerebrium_log

env = os.getenv("ENV", "prod")

_EXAMPLE_MAIN = """
from typing import Optional
from pydantic import BaseModel


class Item(BaseModel):
    # Add your input parameters here
    prompt: str
    your_param: Optional[str] = None # an example optional parameter


def predict(item, run_id, logger):
    item = Item(**item)

    ### ADD YOUR CODE HERE
    my_results = {"prediction": item.prompt, "your_optional_param": item.your_param}
    my_status_code = 200 # if you want to return some status code

    ### RETURN YOUR RESULTS
    return {"my_result": my_results, "status_code": my_status_code} # return your results
"""


def was_provided(param_name: str, param_value: any, defaults: dict[str, any]) -> bool:
    """Check if a parameter was explicitly provided by comparing against its default value."""
    return defaults.get(param_name, object()) != param_value


@cli.command("init")
def init(
    init_dir: Annotated[
        str,
        typer.Argument(
            help="Directory where you would like to init a Cortex project.",
        ),
    ] = ".",
    name: Annotated[
        str, typer.Option(help="Name of the Cortex deployment.")
    ] = "my-cortex-deployment",
    overwrite: Annotated[
        bool, typer.Option(help="Flag to overwrite contents of the init_dir.")
    ] = False,
    requirements_list: Annotated[
        str,
        typer.Option(
            help=(
                "Optional list of requirements. "
                "Example: \"['transformers', 'torch==1.31.1']\""
            ),
        ),
    ] = "['transformers', 'torch>=2.0.0', 'pydantic']",
    pkg_list: Annotated[
        str,
        typer.Option(
            help=("Optional list of apt packages. For example: \"['git', 'ffmpeg' ]\""),
        ),
    ] = "['git', 'ffmpeg' ]",
    conda_pkglist: Annotated[
        str, typer.Option(help="Optional list of conda packages.")
    ] = "",
    gpu: Annotated[
        str,
        typer.Option(
            help=(
                "Hardware to use for the Cortex deployment. "
                "Defaults to 'GPU'. "
                f"Can be one of: {HardwareOptions.available_hardware()} "
            ),
        ),
    ] = "AMPERE_A5000",
    cpu: Annotated[
        int,
        typer.Option(
            min=MIN_CPU,
            max=MAX_CPU,
            help=(
                "Number of CPUs to use for the Cortex deployment. "
                "Defaults to 2. Can be an integer between 1 and 48"
            ),
        ),
    ] = 2,
    memory: Annotated[
        float,
        typer.Option(
            min=MIN_MEMORY,
            max=MAX_MEMORY,
            help=(
                "Amount of memory (in GB) to use for the Cortex deployment. "
                "Defaults to 14.5GB. "
                "Can be a float between 2.0 and 256.0 depending on hardware selection."
            ),
        ),
    ] = DEFAULT_MEMORY,
    gpu_count: Annotated[
        int,
        typer.Option(
            min=0,
            max=MAX_GPU_COUNT,
            help=(
                "Number of GPUs to use for the Cortex deployment. "
                "Defaults to 1. Can be an integer between 1 and 8."
            ),
        ),
    ] = 1,
    include: Annotated[
        str,
        typer.Option(
            help=(
                "Comma delimited string list of relative paths to files/folder to include. "
                "Defaults to all visible files/folders in project root."
            ),
        ),
    ] = DEFAULT_INCLUDE,
    exclude: Annotated[
        str,
        typer.Option(
            help=(
                "Comma delimited string list of relative paths to files/folder to exclude. "
                "Defaults to all hidden files/folders in project root."
            ),
        ),
    ] = DEFAULT_EXCLUDE,
    log_level: Annotated[
        str,
        typer.Option(
            help="Log level for the Cortex deployment. Can be one of 'DEBUG' or 'INFO'",
        ),
    ] = "INFO",
    predict_data: Annotated[
        Optional[str],
        typer.Option(
            help="JSON string containing all the parameters that will be used to run your "
            "deployment's predict function on build to ensure your new deployment will work "
            "as expected before replacing your existing deployment.",
        ),
    ] = None,
    disable_animation: Annotated[
        bool,
        typer.Option(
            help="Whether to use TQDM and yaspin animations.",
        ),
    ] = bool(os.getenv("CI")),
    cuda_version: Annotated[
        str,
        typer.Option(
            help=(
                "CUDA version to use. "
                "Currently, we support 11.8 as '11' and 12.2 as '12'. Defaults to '12'"
            ),
        ),
    ] = "12",
):
    """
    Initialize an empty Cerebrium Cortex project.
    """

    if gpu:
        vals = HardwareOptions.available_hardware()
        if gpu not in vals:
            logging.cerebrium_log(
                message=f"Hardware must be one of {vals}", level="ERROR"
            )
        hardware = getattr(HardwareOptions, gpu).name

    if not os.path.exists(init_dir):
        os.makedirs(init_dir)
    elif os.listdir(init_dir) and not overwrite:
        logging.cerebrium_log(
            level="WARNING",
            message="Directory is not empty. "
            "Use an empty directory or use the `--overwrite` flag.",
            end="\t",
        )

    if not os.path.exists(os.path.join(init_dir, "main.py")):
        with open(os.path.join(init_dir, "main.py"), "w") as f:
            f.write(_EXAMPLE_MAIN)

    config = {
        "name": name,
        "gpu": hardware,
        "cpu": cpu,
        "memory": memory,
        "log_level": log_level,
        "include": include,
        "exclude": exclude,
        "cooldown": DEFAULT_COOLDOWN,
        "gpu_count": gpu_count,
        "predict_data": predict_data
        or '{"prompt": "Here is some example predict data for your cerebrium.toml which will be used to test your predict function on build."}',
        "min_replicas": 0,
        "disable_predict": False,
        "force_rebuild": False,
        "disable_confirmation": False,
        "cuda_version": cuda_version,
    }
    if disable_animation is not None:
        config["disable_animation"] = disable_animation

    requirements_list = requirements_list.strip("[]").split(",")
    requirements_list = [r.strip().strip("'").strip('"') for r in requirements_list]
    pkg_list = pkg_list.strip("[]").split(",")
    pkg_list = [p.strip().strip("'").strip('"') for p in pkg_list]
    conda_pkglist = conda_pkglist.strip("[]").split(",")
    conda_pkglist = [c.strip().strip("'").strip('"') for c in conda_pkglist]
    # if any of the lists only contain an empty string, set to empty list
    requirements_list = (
        {}
        if len(requirements_list) == 1 and requirements_list[0] == ""
        else requirements_list
    )
    pkg_list = {} if len(pkg_list) == 1 and pkg_list[0] == "" else pkg_list
    conda_pkglist = (
        {} if len(conda_pkglist) == 1 and conda_pkglist[0] == "" else conda_pkglist
    )

    utils.legacy_to_toml_structure(
        name=name,
        legacy_config=config,
        config_file=os.path.join(init_dir, "cerebrium.toml"),
        pip=requirements_list,
        apt=pkg_list,
        conda=conda_pkglist,
        overwrite=overwrite,
    )

    print("🚀 Cerebrium Cortex project initialized successfully!")


@cli.command("deploy")
def deploy(
    name: Annotated[str, typer.Option(help="Name of the Cortex deployment.")] = "",
    disable_syntax_check: Annotated[
        bool, typer.Option(help="Flag to disable syntax check.")
    ] = False,
    gpu: Annotated[
        str,
        typer.Option(
            help=(
                "Hardware to use for the Cortex deployment. "
                "Defaults to 'AMPERE_A6000'. "
                "Can be one of "
                "'TURING_4000', "
                "'TURING_5000', "
                "'AMPERE_A4000', "
                "'AMPERE_A5000', "
                "'AMPERE_A6000', "
                "'AMPERE_A100'"
            ),
        ),
    ] = "",
    cpu: Annotated[
        Optional[int],
        typer.Option(
            min=MIN_CPU,
            max=MAX_CPU,
            help=(
                "Number of vCPUs to use for the Cortex deployment. Defaults to 2. "
                "Can be an integer between 1 and 48."
            ),
        ),
    ] = None,
    memory: Annotated[
        Optional[float],
        typer.Option(
            min=MIN_MEMORY,
            max=MAX_MEMORY,
            help=(
                "Amount of memory(GB) to use for the Cortex deployment. Defaults to 16. "
                "Can be a float between 2.0 and 256.0 depending on hardware selection."
            ),
        ),
    ] = None,
    gpu_count: Annotated[
        Optional[int],
        typer.Option(
            min=1,
            max=MAX_GPU_COUNT,
            help=(
                "Number of GPUs to use for the Cortex deployment. Defaults to 1. "
                "Can be an integer between 1 and 8."
            ),
        ),
    ] = None,
    min_replicas: Annotated[
        Optional[int],
        typer.Option(
            min=0,
            max=200,
            help=(
                "Minimum number of replicas to create on the Cortex deployment. "
                "Defaults to 0."
            ),
        ),
    ] = None,
    max_replicas: Annotated[
        Optional[int],
        typer.Option(
            min=1,
            max=200,
            help=(
                "A hard limit on the maximum number of replicas to allow. "
                "Defaults to 2 for free users. "
                "Enterprise and standard users are set to maximum specified in their plan"
            ),
        ),
    ] = None,
    predict_data: Annotated[
        Optional[str],
        typer.Option(
            help="JSON string containing all the parameters that will be used to run your "
            "deployment's predict function on build to ensure your new deployment will work "
            "as expected before replacing your existing deployment.",
        ),
    ] = None,
    python_version: Annotated[
        str,
        typer.Option(
            help=(
                "Python version to use. "
                "Currently, we support '3.8' to '3.11'. Defaults to '3.10'"
            ),
        ),
    ] = "",
    include: Annotated[
        str,
        typer.Option(
            help=(
                "Comma delimited string list of relative paths to files/folder to include. "
                "Defaults to all visible files/folders in project root."
            ),
        ),
    ] = "",
    exclude: Annotated[
        str,
        typer.Option(
            help="Comma delimited string list of relative paths to files/folder to exclude. "
            "Defaults to all hidden files/folders in project root.",
        ),
    ] = "",
    cooldown: Annotated[
        Union[int, None],
        typer.Option(
            help="Cooldown period in seconds before an inactive replica of your deployment is scaled down. Defaults to 60s.",
        ),
    ] = None,
    force_rebuild: Annotated[
        Union[None, bool],
        typer.Option(
            help="Force rebuild. Clears rebuilds deployment from scratch as if it's a clean deployment.",
        ),
    ] = None,
    init_debug: Annotated[
        Union[None, bool],
        typer.Option(
            help="Stops the container after initialization.",
        ),
    ] = None,
    log_level: Annotated[
        Optional[str],
        typer.Option(
            help="Log level for the Cortex deployment. Can be one of 'DEBUG' or 'INFO'",
        ),
    ] = "INFO",
    config_file: Annotated[
        str,
        typer.Option(
            help="Path to cerebrium.toml file. You can generate a config using `cerebrium init-cortex`. The contents of the deployment config file are overridden by the command line arguments.",
        ),
    ] = "",
    disable_confirmation: Annotated[
        bool,
        typer.Option(
            "--disable-confirmation",
            "-q",
            help="Whether to disable the confirmation prompt before deploying.",
        ),
    ] = False,
    disable_predict: Annotated[
        Optional[bool], typer.Option(help="Flag to disable running predict function.")
    ] = None,
    disable_animation: Annotated[
        bool,
        typer.Option(
            help="Whether to use TQDM and yaspin animations.",
        ),
    ] = False,
    disable_build_logs: Annotated[
        bool, typer.Option(help="Whether to disable build logs during a deployment.")
    ] = False,
    hide_public_endpoint: Annotated[
        bool,
        typer.Option(
            help="Whether to hide the public endpoint of the deployment when printing the logs.",
        ),
    ] = False,
    cuda_version: Annotated[
        str,
        typer.Option(
            help=(
                "CUDA version to use. "
                "Currently, we support 11.8 as '11' and 12.2 as '12'. Defaults to '12'"
            ),
        ),
    ] = "",
):
    """
    Deploy a Cortex deployment to Cerebrium
    """

    # func_defaults contains all parameters with their default values
    func_defaults = {
        k: v.default
        for k, v in inspect.signature(deploy).parameters.items()
        if v.default is not inspect.Parameter.empty
    }
    # provided_params only include explicitly provided parameters
    provided_params = {
        param: value
        for param, value in locals().items()
        if param in func_defaults and was_provided(param, value, func_defaults)
    }
    # Merge func_defaults with provided_params. Provided values override default values where applicable.
    final_params = {**func_defaults, **provided_params}

    # load config toml file and merge with param values
    config_obj = utils.merge_config_with_params("cerebrium.toml", final_params)

    ##validation is done with types in classes
    cerebrium_config = CerebriumConfig(
        scaling=CerebriumScaling(**config_obj["scaling"]),
        build=CerebriumBuild(**config_obj["build"]),
        deployment=CerebriumDeployment(**config_obj["deployment"]),
        hardware=CerebriumHardware(**config_obj["hardware"]),
        dependencies=CerebriumDependencies(**config_obj["dependencies"]),
        cerebrium_version=cerebrium_version,
    )

    build_status, setup_response = package_app(cerebrium_config, OperationType.DEPLOY)
    if "success" in build_status:
        project_id = setup_response["projectId"]
        jwt = setup_response["jwt"]

        if env == "prod":
            endpoint = f"https://run.cerebrium.ai/v3/{project_id}/{cerebrium_config.deployment.name}/predict"
        else:
            endpoint = f"https://dev-run.cerebrium.ai/v3/{project_id}/{cerebrium_config.deployment.name}/predict"

        dashboard_url = (
            f"{api.dashboard_url}/projects/{project_id}/models/{project_id}-{name}"
        )

        info_string = (
            f"🔗 [link={dashboard_url}]View your deployment dashboard here[/link]\n"
            f"🔗 [link={dashboard_url}?tab=builds]View builds here[/link]\n"
            f"🔗 [link={dashboard_url}?tab=runs]View runs here[/link]\n\n"
            f"🛜  Endpoint:\n{endpoint}"
        )

        dashboard_info = Panel(
            info_string,
            title=f"[bold green]🚀 {name} is now live! 🚀 ",
            border_style="green",
            width=100,
            padding=(1, 2),
        )

        console(Group(dashboard_info))

        curl_command = colored(
            f"curl -X POST {endpoint} \\\n"
            "     -H 'Content-Type: application/json'\\\n"
            f"     -H 'Authorization: {jwt}'\\\n"
            '     --data \'{"prompt": "Hello World!"}\'',
            "green",
        )
        print(
            "\n💡You can call the endpoint with the following curl command:\n"
            f"{curl_command}"
        )
    elif build_status == "build_failure":
        console(
            Text(f"Unfortunately there was an issue with your deployment", style="red")
        )


@cli.command("build")
def build(
    name: Annotated[str, typer.Option(help="Name of the Cortex deployment.")] = "",
    disable_syntax_check: Annotated[
        bool, typer.Option(help="Flag to disable syntax check.")
    ] = False,
    gpu: Annotated[
        str,
        typer.Option(
            help=(
                "Hardware to use for the Cortex deployment. "
                "Defaults to 'AMPERE_A6000'. "
                "Can be one of "
                "'TURING_4000', "
                "'TURING_5000', "
                "'AMPERE_A4000', "
                "'AMPERE_A5000', "
                "'AMPERE_A6000', "
                "'AMPERE_A100'"
            ),
        ),
    ] = "",
    cpu: Annotated[
        Optional[int],
        typer.Option(
            min=MIN_CPU,
            max=MAX_CPU,
            help=(
                "Number of vCPUs to use for the Cortex deployment. Defaults to 2. "
                "Can be an integer between 1 and 48."
            ),
        ),
    ] = None,
    memory: Annotated[
        Optional[float],
        typer.Option(
            min=MIN_MEMORY,
            max=MAX_MEMORY,
            help=(
                "Amount of memory(GB) to use for the Cortex deployment. Defaults to 16. "
                "Can be a float between 2.0 and 256.0 depending on hardware selection."
            ),
        ),
    ] = None,
    gpu_count: Annotated[
        Optional[int],
        typer.Option(
            min=1,
            max=MAX_GPU_COUNT,
            help=(
                "Number of GPUs to use for the Cortex deployment. Defaults to 1. "
                "Can be an integer between 1 and 8."
            ),
        ),
    ] = None,
    python_version: Annotated[
        str,
        typer.Option(
            help=(
                "Python version to use. "
                "Currently, we support '3.8' to '3.11'. Defaults to '3.10'"
            ),
        ),
    ] = "",
    predict: Annotated[
        Optional[str],
        typer.Option(
            help="JSON string containing all the parameters that will be used to run your "
            "deployment's predict function on build to ensure your new deployment will work "
            "as expected before replacing your existing deployment.",
        ),
    ] = None,
    include: Annotated[
        str,
        typer.Option(
            help=(
                "Comma delimited string list of relative paths to files/folder to include. "
                "Defaults to all visible files/folders in project root."
            ),
        ),
    ] = "",
    exclude: Annotated[
        str,
        typer.Option(
            help="Comma delimited string list of relative paths to files/folder to exclude. Defaults to all hidden files/folders in project root.",
        ),
    ] = "",
    force_rebuild: Annotated[Optional[bool], typer.Option()] = False,
    config_file: Annotated[
        str,
        typer.Option(
            help="Path to cerebrium.toml file. You can generate a config using `cerebrium init-cortex`. The contents of the deployment config file are overridden by the command line arguments.",
        ),
    ] = "",
    log_level: Annotated[
        Optional[str],
        typer.Option(
            help="Log level for the Cortex build. Can be one of 'DEBUG' or 'INFO'"
        ),
    ] = None,
    disable_confirmation: Annotated[
        bool,
        typer.Option(
            help="Whether to disable the confirmation prompt before deploying.",
        ),
    ] = False,
    disable_predict: Annotated[
        Optional[bool], typer.Option(help="Flag to disable running predict function.")
    ] = None,
    disable_animation: Annotated[
        Optional[bool],
        typer.Option(
            help="Whether to use TQDM and yaspin animations.",
        ),
    ] = None,
    disable_build_logs: Annotated[
        bool, typer.Option(help="Whether to disable build logs during a deployment.")
    ] = False,
    hide_public_endpoint: Annotated[
        bool,
        typer.Option(
            help="Whether to hide the public endpoint of the deployment when printing the logs.",
        ),
    ] = False,
    cuda_version: Annotated[
        str,
        typer.Option(
            help=(
                "CUDA version to use. "
                "Currently, we support 11.8 as '11' and 12.2 as '12'. Defaults to '12'"
            ),
        ),
    ] = "12",
):
    """
    Build and run your Cortex files on Cerebrium to verify that they're working as expected.
    """

    # func_defaults contains all parameters with their default values
    func_defaults = {
        k: v.default
        for k, v in inspect.signature(deploy).parameters.items()
        if v.default is not inspect.Parameter.empty
    }
    # provided_params only include explicitly provided parameters
    provided_params = {
        param: value
        for param, value in locals().items()
        if param in func_defaults and was_provided(param, value, func_defaults)
    }
    # Merge func_defaults with provided_params. Provided values override default values where applicable.
    final_params = {**func_defaults, **provided_params}

    # load config toml file and merge with param values
    config_obj = utils.merge_config_with_params("cerebrium.toml", final_params)

    ##validation is done with types in classes
    cerebrium_config = CerebriumConfig(
        scaling=CerebriumScaling(**config_obj["scaling"]),
        build=CerebriumBuild(**config_obj["build"]),
        deployment=CerebriumDeployment(**config_obj["deployment"]),
        hardware=CerebriumHardware(**config_obj["hardware"]),
        dependencies=CerebriumDependencies(**config_obj["dependencies"]),
        cerebrium_version=cerebrium_version,
    )

    build_status = package_app(cerebrium_config, OperationType.RUN)
    if "success" in build_status:
        console(
            Text(
                f"Unfortunately there was an issue with your deployment", style="green"
            )
        )
    elif build_status == "build_failure":
        console(Text(f"Unfortunately there was an issue with your build", style="red"))


@cli.command("upgrade-yaml")
def upgrade_yaml(
    name: Annotated[str, typer.Option(help="Name of the Cortex deployment.")] = "",
    config_file: Annotated[
        str,
        typer.Option(
            help="Path to cerebrium.yaml file. You can generate a config using `cerebrium init-cortex`. The contents of the deployment config file are overridden by the command line arguments.",
        ),
    ] = "",
):
    """Upgrade your config.yaml file to cerebrium.toml"""
    if not config_file:
        config_file = os.path.join(os.getcwd(), "config.yaml")
    if not os.path.exists(config_file):
        logging.cerebrium_log(
            level="ERROR",
            message=f"Config file {config_file} does not exist.",
        )

    config = yaml.safe_load(open(config_file, "r"))
    utils.legacy_to_toml_structure(
        name=name,
        legacy_config=config,
        config_file=config_file,
        save_to_file=True,
        disable_confirmation=True,
    )

    print("🚀 Cerebrium project upgraded successfully!")


def package_app(cerebrium_config: CerebriumConfig, type: OperationType):
    # Get the files in the users directory
    cerebrium_config.file_list = utils.determine_includes(
        include=cerebrium_config.deployment.include,
        exclude=cerebrium_config.deployment.exclude,
    )

    if not cerebrium_config.build.disable_syntax_check:
        verification.run_pyflakes(files=cerebrium_config.file_list, print_warnings=True)

    if cerebrium_config.build.disable_predict:
        cerebrium_config.build.predict_data = None

    cerebrium_config.partial_upload = False
    # If files are larger than 100MB, use partial_upload and localFiles otherwise upload with app zip
    if utils.check_deployment_size(cerebrium_config.file_list, 100):
        if len(cerebrium_config.file_list) < 1000:
            print("📦 Large upload, only uploading files that have changed...")
            cerebrium_config.partial_upload = True
        else:
            cerebrium_log(
                "⚠️ 1000+ files detected. Partial sync not possible. Try reduce the number of files or file size for faster deployments.",
                level="ERROR",
            )
            exit()

    if cerebrium_config.partial_upload:
        setup_response = do_partial_upload(cerebrium_config, type=type)
    else:
        params = utils.flatten_cerebrium_config_to_json(config=cerebrium_config)
        params["function"] = type.value
        setup_response = _setup_request(cerebrium_config, params)

    print(f"🆔 Build ID: {setup_response['buildId']}")
    build_status = str(setup_response["status"])

    if build_status == "pending":
        if not cerebrium_config.partial_upload:
            api.upload_cortex_files(
                upload_url=setup_response["uploadUrl"],
                zip_file_name=setup_response["keyName"],
                config=cerebrium_config,
            )

        build_status = "Build pending..."
        start_time = time.time()

        spinner = Spinner("dots", "Building App...", style="gray")

        # This is used to stop the logs on a different thread
        start_event = threading.Event()
        stop_event = threading.Event()

        # if env == "local":
        log_thread = threading.Thread(
            target=api.poll_build_logs,
            args=(
                setup_response["buildId"],
                start_event,
                stop_event,
            ),
        )
        # else:
        #     log_thread = threading.Thread(target=api.stream_logs, args=(start_event, stop_event, f'{setup_response["projectId"]}-{cerebrium_config.deployment.name}', setup_response['buildId']))

        log_thread.start()
        # with yaspin(Spinners.arc, text=build_status, color="magenta") as spinner:
        live = Live(spinner, console=logging.console, refresh_per_second=10)

        # Start the Live context using the start() method
        live.start()
        try:
            while True:
                build_status = api.get_build_status(setup_response["buildId"])
                spinner.text = api.log_build_status(build_status, start_time)
                if build_status in ["success", "build_failure", "init_failure"]:
                    start_event.wait()
                    live.update(Text(""))
                    stop_event.set()
                    break
                time.sleep(5)
        finally:
            # Stop the Live instance after the loop
            live.stop()

        log_thread.join()
    elif build_status == "running":
        print("🤷 No file changes detected. Not fetching logs")
    else:
        spinner.stop(text="Build failed")
        cerebrium_log("ERROR", "Build failed.")

    return build_status, setup_response


def do_partial_upload(
    cerebrium_config: CerebriumConfig, type: OperationType
) -> Dict[str, Any]:
    """
    Partial uploads need to be done in a different flow to the normal upload.

    This function will:
    - Make a temporary directory
    - Copy all the user's files into the temporary directory
    - Create all utility files (requirements.txt, apt.txt, conda.txt, _cerebrium_predict.json, etc) and remove any conflicting files
    - Get the hashes of all the files in the temporary directory
    - Compare the hashes to the hashes of the last deployment
    - Upload the files that have changed
    - Delete the temporary directory
    - Create a marker file with the hashes of the new files

    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # copy all files in the user's file list to the temp dir
        temp_file_list: List[str] = []
        for file in cerebrium_config.file_list:
            real_file_path = os.path.realpath(file)
            rel_path = os.path.relpath(real_file_path, os.getcwd())
            temp_file = os.path.join(temp_dir, rel_path)
            os.makedirs(os.path.dirname(temp_file), exist_ok=True)
            shutil.copy(file, temp_file)
            temp_file_list.append(temp_file)

        # make utility files
        sync_files.make_cortex_util_files(temp_dir=temp_dir, config=cerebrium_config)

        temp_file_list.extend(
            [os.path.join(temp_dir, f) for f in datatypes.INTERNAL_FILES]
        )

        cerebrium_config.local_files = sync_files.gather_hashes(
            temp_file_list, temp_dir
        )

        params = utils.flatten_cerebrium_config_to_json(config=cerebrium_config)
        params["function"] = type.value
        setup_response = _setup_request(cerebrium_config, params)

        if setup_response["status"] == "pending":
            uploaded_count = upload_files_to_s3(
                setup_response["uploadUrls"], base_dir=temp_dir
            )
            upload_marker_file_and_delete(
                setup_response["markerFile"], uploaded_count, setup_response["buildId"]
            )

    return setup_response


def _setup_request(
    cerebrium_config: CerebriumConfig,
    params: Dict[str, Any],
) -> Dict[str, Any]:
    # Include the predict data in the content hash to trigger a rebuild if the predict changes
    files_hash = utils.content_hash(
        cerebrium_config.file_list, strings=cerebrium_config.build.predict_data
    )
    params["upload_hash"] = files_hash

    if not utils.confirm_deployment(
        cerebrium_config, "deploy", cerebrium_config.build.disable_confirmation
    ):
        sys.exit()

    setup_response = cerebrium_request(HttpMethod.POST, "setupApp", params)
    if setup_response is None:
        cerebrium_log(
            level="ERROR",
            message="There was an error deploying your app. Please try again.",
            prefix="",
        )
        exit()

    if setup_response.status_code != 200:
        cerebrium_log(
            level="ERROR",
            message=f"There was an error deploying your app\n{setup_response.json()['message']}",
            prefix="",
        )
        exit()

    return setup_response.json()
