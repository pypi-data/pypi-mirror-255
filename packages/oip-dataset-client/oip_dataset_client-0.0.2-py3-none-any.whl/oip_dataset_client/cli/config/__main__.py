""" Open Innovation Dataset Client configuration wizard"""
from argparse import ArgumentParser
from pathlib import Path
import os
import re
import ast
from typing import Dict, Optional
from oip_dataset_client.HttpClient import HttpClient
from oip_dataset_client.schema import ApiRequestArgs
from oip_dataset_client.ServerConf import SERVER_MODULE_NAME, WORKSPACE_ENTITY_NAME


def main():
    """setting up the oip-dataset-client"""

    arg_parser: ArgumentParser = ArgumentParser(description=__doc__)
    print("Open Innovation Dataset SDK setup process")
    args = arg_parser.parse_args()
    conf_file = Path(os.path.expanduser(args.file)).absolute()
    conf_folder: Path = conf_file.parent
    if not conf_folder.exists():
        conf_folder.mkdir(exist_ok=True)
    oip_credentials = prompt_oip_credentials()
    if oip_credentials:
        os.environ["OIP_API_HOST"] = oip_credentials["api_host"]
        os.environ["OIP_API_KEY"] = oip_credentials["api_key"]
        os.environ["OIP_WORKSPACE_ID"] = oip_credentials["workspace_id"]
        os.environ["OIP_WORKSPACE_NAME"] = oip_credentials["workspace_name"]


def prompt_oip_credentials() -> Optional[Dict[str, str]]:
    """
    :return: dict: open innovation credentials example:
        {api_host:oip_host,
        api_key:your_api_key,
        workspace_name:your_workspace_name,
        workspace_id:your_workspace_id}
    """
    description = (
        "\n"
        "Please navigate to the Workspace page within the `Open Innovation web application`.\n"
        "Select your desired workspace, then click on `Create new credentials`.\n"
        "Afterward, click on `Copy to clipboard.` Finally, paste the copied configuration here:\n"
    )
    print(description)
    parse_input: str = ""
    if os.environ.get("JPY_PARENT_PID"):
        # When running from a colab instance and calling oip-dataset-client-init
        # colab will squish the api credentials into a single line
        # The regex splits this single line based on 2 spaces or more
        api_input = input()
        parse_input = "\n".join(re.split(r" {2,}", api_input))
    else:
        for line in iter(input, ""):
            parse_input += line + "\n"
            if line.rstrip() == "}":
                break
    try:
        parsed_input = ast.literal_eval(parse_input)
    except:
        raise Exception(
            "You need to copy and paste the correct configuration exactly as it appears on the website"
        )

    api_host: str = parsed_input.get("api_host", None)
    api_key: str = parsed_input.get("api_key", None)
    workspace_name: str = parsed_input.get("workspace", None)
    # print message to the consol and exist if any issue happen
    workspace_id: Optional[str] = get_workspace_id(api_host, api_key, workspace_name)
    if workspace_id:
        oip_credentials: Dict[str, str] = {
            "api_host": api_host,
            "api_key": api_key,
            "workspace_name": workspace_name,
            "workspace_id": workspace_id,
        }
        return oip_credentials
    else:
        return None


def get_workspace_id(api_host: str, api_key: str, workspace_name: str) -> Optional[str]:
    """
    Retrieve workspace id from the server api based on the provided parameters.
    :param api_host: str: The API Host
    :param api_key: str: The API Key
    :param workspace_name: str: The workspace name
    :return: str: Workspace ID.
    """
    url: str = os.path.join(api_host, SERVER_MODULE_NAME, WORKSPACE_ENTITY_NAME)
    url = url.replace("\\", "/")
    headers: Dict[str, str] = {"authorization": "APIKey " + api_key}
    api_request_args: ApiRequestArgs = {
        "filter_cols": "name",
        "filter_ops": "=",
        "filter_vals": workspace_name,
    }
    response = HttpClient.get(url, headers, api_request_args)
    if response.status_code == 200 and response.json()["data"]:
        return response.json()["data"][0]["id"]
    else:
        print(
            f"{workspace_name} is not a valid workspace please verify it and try again"
        )
        exit(1)


if __name__ == "__main__":
    main()
