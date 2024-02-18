class CerebriumRequestError(Exception):
    """
    Class to handle the error code messages from the Cerebrium API.

    Args:
        status_code (int): The status code returned from the Cerebrium API.
        endpoint (str): The endpoint that was called.
    """

    def __init__(self, status_code, endpoint, data={}):
        # sourcery skip: default-mutable-arg
        self.status_code = status_code
        self.endpoint = endpoint
        self.data = data
        super().__init__(self.status_code)

    def __str__(self):
        msg = f"{self.status_code} on `{self.endpoint}`\n"

        if self.status_code == 401:
            msg += "API key does not exist or is incorrect."
            msg += "If your key is correct, please contact the Cerebrium team."
        elif self.status_code == 403:
            if plan_limits := self.data.get("planLimits"):
                can_deploy_model = plan_limits.get("canDeployModel")
                model_limit = plan_limits.get("numberOfPlanModels")
                upgrade_link = plan_limits.get("upgradeLink")
                if not can_deploy_model:
                    msg = f"You have exceeded your deployment limit of {model_limit}."
                    msg += f" Please upgrade your Cerebrium plan at `{upgrade_link}`"
        elif str(self.status_code)[0] == "4":
            specific_message = (
                ""
                if isinstance(self.data, str)
                else " " + self.data.get("message", "") + "."
            )
            msg = f"API Call Failed.{specific_message}"
        elif self.status_code == 500:
            msg = f"Internal Server Error: {self.data}."
        elif self.status_code == 502:
            msg = "Bad Gateway."
        return msg
