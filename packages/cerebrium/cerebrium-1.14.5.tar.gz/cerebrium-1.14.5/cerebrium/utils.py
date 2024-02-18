import copy
import fnmatch
import hashlib
import inspect
import os
import re
import yaml
import toml
import typer
from typing import Callable, Dict, List, Union, Any
from rich.panel import Panel
from rich import box
from rich.table import Table
from rich import print as console
from termcolor import colored
from cerebrium.logging import cerebrium_log

from cerebrium.datatypes import *

env = os.getenv("ENV", "prod")
RequirementsType = Union[Dict[str, str], List[str]]


def determine_includes(include: str, exclude: str):
    include_set = include.strip("[]").split(",")
    include_set.extend(
        [
            "./main.py",
            "./requirements.txt",
            "./pkglist.txt",
            "./conda_pkglist.txt",
        ]
    )
    include_set = set(map(ensure_pattern_format, include_set))
    include_set = [i.strip() for i in include_set]

    exclude_set = exclude.strip("[]").split(",")
    exclude_set = [e.strip() for e in exclude_set]
    exclude_set = set(map(ensure_pattern_format, exclude_set))

    file_list: List[str] = []
    for root, _, files in os.walk("./"):
        for file in files:
            full_path = os.path.join(root, file)
            if any(
                fnmatch.fnmatch(full_path, pattern) for pattern in include_set
            ) and not any(
                fnmatch.fnmatch(full_path, pattern) for pattern in exclude_set
            ):
                print(f"➕ Adding {full_path}")
                file_list.append(full_path)
    return file_list


def get_api_key():
    config_path = os.path.expanduser("~/.cerebrium/config.yaml")
    msg = "Please login using 'cerebrium login"
    if not os.path.exists(config_path):
        cerebrium_log(level="ERROR", message=msg)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    if env == "dev":
        print("❗️❗️Logging in with dev API key❗️❗️")
        key_name = "dev_api_key"
    else:
        key_name = "api_key"

    if config is None or key_name not in config:
        cerebrium_log(level="ERROR", message=msg)

    return config[key_name]


def get_current_project_context():
    """
    Get the current project context and project name
    """
    config_path = os.path.expanduser("~/.cerebrium/config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            key_name = ""
            if env != "prod":
                key_name = f"{env}-"
            if config.get(f"{key_name}project"):
                return config.get(f"{key_name}project")
    print("No current project context found.")
    return None, None


def ensure_pattern_format(pattern: str):
    if not pattern.startswith("./"):
        pattern = f"./{pattern}"
    elif pattern.startswith("/"):
        cerebrium_log(
            prefix="ValueError",
            level="Error",
            message="Pattern cannot start with a forward slash. Please use a relative path.",
        )
    if pattern.endswith("/"):
        pattern = f"{pattern}*"
    elif os.path.isdir(pattern) and not pattern.endswith("/"):
        pattern = f"{pattern}/*"
    return pattern


def remove_null_values(param_dict: Dict[str, Any]):
    new_dict = {}
    for key, val in param_dict.items():
        if isinstance(val, dict):
            val = remove_null_values(val)
        if val is not None:
            if not (isinstance(val, str) and val == ""):
                new_dict[key] = val
    return new_dict


def content_hash(
    files: Union[str, List[str]], strings: Union[List[str], str, None] = None
) -> str:
    """
    Hash the content of each file, avoiding metadata.
    """

    files = files if isinstance(files, list) else [files]
    h = hashlib.sha256()
    if files:
        for file in files:
            if os.path.exists(file):
                with open(file, "rb") as f:
                    h.update(f.read())
            else:
                return "FILE_DOESNT_EXIST"
    if strings is not None:
        if not isinstance(strings, list):
            strings = [strings]
        for string in strings:
            if isinstance(string, str):  # tyoe: ignore
                h.update(string.encode())
    if files or strings:
        return h.hexdigest()
    return "NO_FILES"


def check_deployment_size(files: List[str], max_size_mb: int = 100):
    """
    Check if the sum of all files is less than max_size MB
    """
    files = files if isinstance(files, list) else [files]
    total_size = 0
    for file in files:
        if os.path.exists(file):
            total_size += os.path.getsize(file)

    return total_size > max_size_mb * 1024 * 1024


def confirm_deployment(
    config: CerebriumConfig,
    cerebrium_function: str,
    disable_confirmation: bool = False,
):
    """
    Print out a confirmation message for the deployment
    - Display selected hardware options and configuration on a panel
    - Ask user to confirm
    """
    hardware = config.hardware
    deployment = config.deployment
    scaling = config.scaling
    build = config.build
    dependencies = config.dependencies

    def addOptionalRow(key, value):
        if value:
            deployment_table.add_row(key, str(value))

    deployment_table = Table(box=box.SIMPLE_HEAD)
    deployment_table.add_column("Parameter", style="")
    deployment_table.add_column("Value", style="")

    deployment_table.add_row("HARDWARE PARAMETERS", "", style="bold")
    deployment_table.add_row("GPU", str(hardware.gpu))
    deployment_table.add_row("CPU", str(hardware.cpu))
    deployment_table.add_row("Memory", str(hardware.memory))
    if hardware.gpu != "CPU":
        deployment_table.add_row("GPU Count", str(hardware.gpu_count))

    deployment_table.add_row("", "")
    if cerebrium_function == "run":
        deployment_table.add_row("RUN PARAMETERS", "", style="bold")
    else:
        deployment_table.add_row("DEPLOYMENT PARAMETERS", "", style="bold")
    deployment_table.add_row("Python Version", str(deployment.python_version))
    deployment_table.add_row("Include pattern", str(deployment.include))
    deployment_table.add_row("Exclude pattern", str(deployment.exclude))
    deployment_table.add_row("CUDA Version", str(deployment.cuda_version))

    deployment_table.add_row("", "")
    deployment_table.add_row("SCALING PARAMETERS", "", style="bold")
    deployment_table.add_row("Cooldown", str(scaling.cooldown))
    deployment_table.add_row("Minimum Replicas", str(scaling.min_replicas))
    if scaling.max_replicas is not None:
        deployment_table.add_row("Maximum Replicas", str(scaling.max_replicas))

    deployment_table.add_row("", "")
    deployment_table.add_row("BUILD PARAMETERS", "", style="bold")
    if build.log_level is not None:
        deployment_table.add_row("Log Level", str(build.log_level))
    if build.predict_data is not None:
        predict_data = str(build.predict_data)
        if len(predict_data) > 180:
            predict_data = predict_data[:180] + "..."
        deployment_table.add_row("Predict Data", predict_data)

    for key, value in build.__dict__.items():
        if key not in ["predict_data", "log_level"]:
            addOptionalRow(key, value)

    deployment_table.add_row("", "")
    deployment_table.add_row("DEPENDENCIES", "", style="bold")

    deployment_table.add_row(
        "pip", "".join(req_dict_to_str_list(dependencies.pip, for_display=True))
    )
    deployment_table.add_row(
        "apt", "".join(req_dict_to_str_list(dependencies.apt, for_display=True))
    )
    deployment_table.add_row(
        "conda", "".join(req_dict_to_str_list(dependencies.conda, for_display=True))
    )

    name = deployment.name
    config_options_panel = Panel.fit(
        deployment_table,
        title=f"[bold]🧠 Deployment parameters for {name} 🧠",
        border_style="yellow bold",
        width=100,
        padding=(1, 2),
    )
    print()
    console(config_options_panel)
    print()
    if not disable_confirmation:
        return typer.confirm(
            "Do you want to continue with the deployment?",
            default=True,
            show_default=True,
        )
    else:
        return True


def legacy_to_toml_structure(
    name: str,
    legacy_config: Dict[str, Any],
    config_file: str,
    save_to_file: bool = True,
    pip: Dict[str, str] = {},
    apt: List[str] = [],
    conda: Dict[str, str] = {},
    disable_confirmation: bool = False,
    overwrite: bool = False,
) -> CerebriumConfig:
    # Tomls have the following format so they're less intimidating:
    # [cerebrium.hardware]
    # {all the hardware params like cpu, memory, etc}
    # [cerebrium.scaling]
    # {all the scaling params. Min/max replicas, cooldown, etc}
    # [cerebrium.deployment]
    # {all the deployment params. Python version, include, exclude, etc}
    # [cerebrium.requirements] (optional pip requirements)
    # {all the pip requirements}
    # [cerebrium.conda_requirements] (optional conda requirements)
    # {all the conda requirements}
    # [cerebrium.pkglist] (optional pkglist)

    """Upgrade legacy config file to use a more intuitive toml format"""
    legacy = ".yaml" in config_file or ".yml" in config_file

    upgrade_to_toml = False
    if legacy and not disable_confirmation:
        upgrade_prompt = colored(
            "Upgrade legacy config to toml?",
            "yellow",
        )
        if typer.confirm(upgrade_prompt):
            upgrade_to_toml = True
    dir_path = os.path.dirname(os.path.realpath(config_file))
    legacy_config = legacy_config or {}
    new_config = {}

    # Hardware
    hardware = CerebriumHardware(
        gpu=legacy_config.get("hardware" if legacy else "gpu", DEFAULT_GPU_SELECTION),
        cpu=legacy_config.get("cpu", DEFAULT_CPU),
        memory=legacy_config.get("memory", DEFAULT_MEMORY),
        gpu_count=legacy_config.get("gpu_count", DEFAULT_GPU_COUNT),
    )

    deployment = CerebriumDeployment(
        name=legacy_config.get("name") or name,
        python_version=legacy_config.get("python_version", DEFAULT_PYTHON_VERSION),
        include=legacy_config.get("include", DEFAULT_INCLUDE),
        exclude=legacy_config.get("exclude", DEFAULT_EXCLUDE),
    )

    default_predict_data = '{"prompt": "Here is some example predict data for your config.yaml which will be used to test your predict function on build."}'
    build = CerebriumBuild(
        predict_data=legacy_config.get("predict_data", default_predict_data),
        disable_predict=legacy_config.get("disable_predict")
        or legacy_config.get("disable_predict_data"),
        disable_build_logs=legacy_config.get("disable_build_logs"),
        disable_animation=legacy_config.get("disable_animation"),
        force_rebuild=legacy_config.get("force_rebuild"),
        disable_confirmation=legacy_config.get("disable_confirmation"),
        hide_public_endpoint=legacy_config.get("hide_public_endpoint"),
        disable_syntax_check=legacy_config.get("disable_syntax_check"),
    )

    # Scaling
    scaling = CerebriumScaling(
        min_replicas=legacy_config.get("min_replicas", DEFAULT_MIN_REPLICAS),
        max_replicas=legacy_config.get("max_replicas", DEFAULT_MAX_REPLICAS),
        cooldown=legacy_config.get("cooldown", DEFAULT_COOLDOWN),
    )

    # Requirements
    dependencies = {"pip": pip, "conda": conda, "apt": apt}
    if (
        os.path.exists(os.path.join(dir_path, "requirements.txt"))
        and os.stat(os.path.join(dir_path, "requirements.txt")).st_size != 0
        and legacy
    ):
        dependencies = update_from_file(
            "requirements.txt",
            dependencies,
            "pip",
            confirm=(not legacy) and (not disable_confirmation),
        )
        dependencies["pip"].update(req_list_to_dict(pip))
    else:
        dependencies["pip"] = req_list_to_dict(pip)
    if (
        os.path.exists(os.path.join(dir_path, "pkglist.txt"))
        and os.stat(os.path.join(dir_path, "pkglist.txt")).st_size != 0
        and legacy
    ):
        dependencies = update_from_file(
            "pkglist.txt",
            dependencies,
            "apt",
            confirm=(not legacy) and (not disable_confirmation),
        )
        dependencies["apt"].update(req_list_to_dict(apt))

    else:
        dependencies["apt"] = req_list_to_dict(
            apt
        )  # no versions for apt. So we just add the list

    if (
        os.path.exists(os.path.join(dir_path, "conda_pkglist.txt"))
        and os.stat(os.path.join(dir_path, "conda_pkglist.txt")).st_size != 0
        and legacy
    ):
        dependencies = update_from_file(
            "conda_pkglist.txt",
            dependencies,
            "conda",
            confirm=(not legacy) and (not disable_confirmation),
        )
        dependencies["conda"].update(req_list_to_dict(conda))
    else:
        dependencies["conda"] = req_list_to_dict(conda)

    new_config = CerebriumConfig(
        hardware=hardware,
        deployment=deployment,
        scaling=scaling,
        build=build,
        dependencies=CerebriumDependencies(**dependencies),
    )

    if name:
        new_config.deployment.name = name
    elif not new_config.deployment.name:
        new_config.deployment.name = os.path.basename(dir_path)

    if save_to_file or upgrade_to_toml:
        new_config_file = os.path.join(dir_path, "cerebrium.toml")
        save_config_to_toml_file(new_config, new_config_file, overwrite=overwrite)
        # move old config file to config.yaml.legacy
        if legacy:
            cwd = os.getcwd()
            if os.path.exists(config_file):
                os.rename(config_file, config_file + ".legacy")
            elif os.path.exists(os.path.join(cwd, "config.yaml")):
                os.rename(
                    os.path.join(cwd, "config.yaml"),
                    os.path.join(cwd, "config.yaml.legacy"),
                )

    return new_config


def save_config_to_toml_file(
    config: CerebriumConfig, file: str, overwrite: bool = False
):
    # Write to file
    config_dict = copy.deepcopy(config)
    config_dict = config_dict.to_dict()
    if "local_files" in config_dict:
        config_dict.pop("local_files")
    if "cerebrium_version" in config_dict:
        config_dict.pop("cerebrium_version")
    if "api_key" in config_dict:
        config_dict.pop("api_key")
    if "partial_upload" in config_dict:
        config_dict.pop("partial_upload")

    if "init_debug" in config_dict.get("build", {}):
        config_dict["build"].pop("init_debug")

    for k, v in config_dict.items():
        if hasattr(v, "to_dict"):
            config_dict[k] = v.to_dict()

    # sort the keys
    keys = list(config_dict.keys())
    keys.sort()
    config_dict = {k: config_dict[k] for k in keys}
    # make sure "requirements" is last key
    config_dict["dependencies"] = config_dict.pop("dependencies")
    config_dict = {"cerebrium": config_dict}

    if os.path.splitext(file)[1] != ".toml":
        file = os.path.splitext(file)[0] + ".toml"

    if os.path.exists(file):
        if not overwrite:
            cerebrium_log(
                level="WARNING",
                message="cerebrium.toml already exists. Not writing.",
                end="\t",
            )
            return None

    print(f"Saving to {file}")
    with open(file, "w") as f:
        toml.dump(config_dict, f)

    comment = (
        "# This file was automatically generated by Cerebrium as a "
        "starting point for your project. \n"
        "# You can edit it as you wish.\n"
        "# If you would like to learn more about your Cerebrium config, "
        "please visit https://docs.cerebrium.ai/cerebrium/environments/config-files#config-file-example"
    )

    # prepend comment to file
    with open(file, "r") as f:
        content = f.read()
    with open(file, "w") as f:
        f.write(f"{comment}\n\n{content}")


def load_toml(config_file: str) -> dict[str, Any]:
    with open(config_file, "r") as f:
        config_dict = toml.load(f)

    return config_dict


def get_function_params(function: Callable[..., Any]) -> dict[str, Any]:
    """
    Get the parameters of a function
    """
    return {
        k: v.default
        for k, v in inspect.signature(function).parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def merge_config_with_params(config_file: str, params: Dict[str, Any]) -> dict:
    """
    Load the configuration from a TOML file and override it with any non-default parameter values provided.
    This version is enhanced to explicitly handle the nested structure of the cerebrium.toml configuration.

    :param config_file: Path to the TOML configuration file.
    :param params: Keyword arguments corresponding to the deploy function parameters.
    :return: A dictionary with the merged configuration.
    """

    # Load the configuration from the TOML file
    toml_config = load_toml(config_file)["cerebrium"]

    # Define the top-level sections in the TOML configuration
    top_level_sections = {
        "build": get_function_params(CerebriumBuild.__init__),
        "deployment": get_function_params(CerebriumDeployment.__init__),
        "hardware": get_function_params(CerebriumHardware.__init__),
        "scaling": get_function_params(CerebriumScaling.__init__),
        "dependencies": get_function_params(CerebriumDependencies.__init__),
    }

    # Iterate over each top-level section in the TOML configuration
    for section, defaults in top_level_sections.items():
        # check if the key is in the params
        for key, val in defaults.items():
            if key in params and params[key] is not None and params[key] != "":
                toml_config[section][key] = params[key]
            elif toml_config.get(section, {}).get(key) is None:
                # Replace none with default value
                toml_config[section][key] = val
            elif section not in toml_config:
                toml_config[section] = {key: val}

    return toml_config


def flatten_cerebrium_config_to_json(config: CerebriumConfig):
    """
    Takes a CerebriumConfig class object and flattens it into a flat JSON-like dictionary.

    :param config: CerebriumConfig object
    :return: Flat dictionary representing the config
    """
    params = {
        "name": config.deployment.name,
        "cooldown": config.scaling.cooldown,
        "cerebrium_version": config.cerebrium_version,
        "min_replicas": config.scaling.min_replicas,
        "max_replicas": config.scaling.max_replicas,
        "hardware": f"{config.hardware.gpu}",
        "gpu_count": config.hardware.gpu_count,
        "cpu": config.hardware.cpu,
        "memory": config.hardware.memory,
        "python_version": config.deployment.python_version,
        "requirements_hash": content_hash(
            files=[], strings=str(config.dependencies.pip)
        ),
        "pkglist_hash": content_hash(files=[], strings=str(config.dependencies.apt)),
        "conda_pkglist_hash": content_hash(
            files=[], strings=str(config.dependencies.conda)
        ),
        "force_rebuild": config.build.force_rebuild,
        "init_debug": config.build.init_debug,
        "log_level": config.build.log_level,
        "disable_animation": config.build.disable_animation,
        "disable_build_logs": config.build.disable_build_logs,
        "disable_syntax_check": config.build.disable_syntax_check,
        "hide_public_endpoint": config.build.hide_public_endpoint,
        "predict_data": config.build.predict_data,
        "disable_predict": config.build.disable_predict,
        "partial_upload": config.partial_upload,
        "local_files": config.local_files,
    }

    # Remove keys with None values to clean up the dictionary
    params: Dict[str, Any] = {k: v for k, v in params.items() if v is not None}
    return params


def parse_requirements(file: str):
    """Takes a pip requirements file or a pkglist file and returns a list of packages"""
    if not os.path.exists(file):
        cerebrium_log(
            level="ERROR",
            message=f"Could not find {file}. Please create it and try again.",
        )
    with open(file, "r") as f:
        requirements = f.read()
    requirements_list = requirements.split("\n")
    requirements_list = [r.strip() for r in requirements_list]

    # ignore comments
    requirements_list = [r for r in requirements_list if not r.startswith("#")]
    # remove empty lines
    requirements_list = [r for r in requirements_list if r != ""]

    # if there's version numbers, we return a dict of package: version
    # otherwise we return a list of packages
    requirements_dict = req_list_to_dict(requirements_list)
    return requirements_dict


def req_list_to_dict(requirements: List[str]) -> Dict[str, str]:
    """Takes a list of requirements and returns a dict of package: version"""
    requirements_dict: Dict[str, str] = {}
    if len(requirements) == 0:
        return requirements_dict
    for r in requirements:
        # find on "==" or ">=" or "<=" or "~=" or "!=" or ">" or "<"
        search = re.search(r"==|>=|<=|~=|!=|>|<", r)
        if search is None:
            package, version = r, "latest"
        else:
            idx = search.start()
            package, version = r[:idx], r[idx:]
        requirements_dict[package] = version
    return requirements_dict


def req_dict_to_str_list(
    requirements: RequirementsType, for_display: bool = False
) -> List[str]:
    """Takes a dict of requirements and returns a list of requirements to be written to a file"""
    reqs: List[str] = []
    # if version starts with ==, >=, <=, ~=, !=, >, <, we don't add the ==
    # find >=, <=, ~=, !=, >, <
    pattern = re.compile(r"==|>=|<=|~=|!=|>|<")
    if isinstance(requirements, list):
        requirements = req_list_to_dict(requirements)
    for package, version in requirements.items():
        if str(version).lower() == "latest" and not for_display:
            version = ""
        if pattern.search(version):
            reqs.append(f"{package}{version}\n")
        else:
            if version == "":
                reqs.append(f"{package}\n")
            else:
                version = version.strip("=")
                if version.startswith("git+"):
                    reqs.append(f"{version}\n")
                else:
                    reqs.append(f"{package}=={version}\n")

    return reqs


def requirements_to_file(requirements: RequirementsType, file: str) -> None:
    """Takes a dict/list of requirements and writes them to a file"""
    reqs = req_dict_to_str_list(requirements)
    with open(file, "w") as f:
        f.writelines(reqs)


def update_from_file(
    file: str,
    toml_requirements: Dict[str, Dict[str, str]],
    key: str,
    confirm: bool = False,
) -> Dict[str, Dict[str, str]]:
    """Update the requirements dictionary from a file"""
    new_requirements = parse_requirements(file)

    if new_requirements != toml_requirements.get(key):
        if confirm:
            if typer.confirm(
                colored(
                    f"Update {key} requirements in the cerebrium.toml?",
                    "yellow",
                )
            ):
                toml_requirements[key] = new_requirements
            else:
                return toml_requirements
        else:
            toml_requirements[key] = new_requirements

    return toml_requirements
