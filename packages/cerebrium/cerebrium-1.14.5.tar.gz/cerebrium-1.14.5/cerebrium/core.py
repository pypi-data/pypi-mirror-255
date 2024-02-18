import json
import os
import yaml
from typer import Typer
from cerebrium.logging import cerebrium_log

cli = Typer()

IS_SERVER = os.getenv("IS_SERVER", "false")
if os.path.exists("secrets.json"):
    with open("secrets.json") as f:
        SECRETS = json.load(f)
elif os.path.exists("secrets.yaml"):
    with open("secrets.yaml") as f:
        SECRETS = yaml.load(f, Loader=yaml.FullLoader)
else:
    SECRETS = {}


def get_secret(key):
    secret = SECRETS.get(key, "") if SECRETS else os.getenv(key, "")
    if secret == "":
        cerebrium_log(
            level="ERROR",
            message=f"Secret not found for key: {key}, please check your environment variables.",
        )
    else:
        return secret
