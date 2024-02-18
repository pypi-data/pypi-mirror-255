import os
import yaml
import time
from yaspin import yaspin
from yaspin.spinners import Spinners

from cerebrium.api import cerebrium_request, HttpMethod
from cerebrium.utils import env
from cerebrium.core import cli
import platform


@cli.command("login")
def login():
    """
    Authenticate user via oAuth and store token in ~/.cerebrium/config.yaml
    """

    auth_response = cerebrium_request(
        HttpMethod.POST, "device-authorization", {}, False
    )
    auth_response = auth_response.json()["deviceAuthResponsePayload"]
    verification_uri = auth_response["verification_uri_complete"]

    print("You will be redirected to a URL to be authenticated")
    if platform.system() == "Windows":
        os.system(f"start {verification_uri}")
    else:
        os.system(f"open {verification_uri}")

    start_time = time.time()
    while time.time() - start_time < 300:  # 5 minutes
        with yaspin(
            Spinners.arc, text="Waiting for authentication...", color="magenta"
        ):
            response = cerebrium_request(
                HttpMethod.POST,
                "token",
                {"device_code": auth_response["device_code"]},
                False,
            )
            if response.status_code != 400:
                break
            time.sleep(2)

    if response.status_code == 500:
        print(auth_response.json()["message"])
        return
    if response.status_code == 200:
        config_path = os.path.expanduser("~/.cerebrium/config.yaml")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}

        key_name = ""
        if env == "dev":
            print("❗️❗️Logging in with dev API key❗️❗️")
            key_name = "dev-"
        config[f"{key_name}accessToken"] = response.json()["accessToken"]
        config[f"{key_name}refreshToken"] = response.json()["refreshToken"]
        if env == "local":
            print("❗️❗️Logging in with local API key❗️❗️")
            key_name = "local-"
        config[f"{key_name}accessToken"] = response.json()["accessToken"]
        config[f"{key_name}refreshToken"] = response.json()["refreshToken"]

        print("✅  Logged in successfully.")
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        projects_response = cerebrium_request(HttpMethod.GET, "projects", {}, True)
        if projects_response.status_code == 200:
            projects = projects_response.json()["projects"]
            config[f"{key_name}project"] = projects[0]["projectId"]
            print(f"Current project context set to ID: {config.get('project')}")

        with open(config_path, "w") as f:
            yaml.dump(config, f)


@cli.command("save-auth-config")
def save_auth_config(access_token: str, refresh_token: str, project_id: str):
    """
    Saves the access token, refresh token, and project ID to the config file. This function is a helper method to allow users to store credentials directly for the framework. Mostly used for CI/CD
    """
    config_path = os.path.expanduser("~/.cerebrium/config.yaml")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}

    key_name = ""
    if env == "dev":
        print("❗️❗️Logging in with dev API key❗️❗️")
        key_name = "dev-"
    if env == "local":
        print("❗️❗️Logging in with local API key❗️❗️")
        key_name = "local-"

    config[f"{key_name}accessToken"] = access_token
    config[f"{key_name}refreshToken"] = refresh_token
    config[f"{key_name}project"] = project_id

    with open(config_path, "w") as f:
        yaml.dump(config, f)
    print("✅ Configuration saved successfully.")
