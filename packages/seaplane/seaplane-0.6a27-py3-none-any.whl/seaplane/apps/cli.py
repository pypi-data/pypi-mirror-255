"""
command line interface
"""
from argparse import ArgumentParser
from importlib.metadata import version
import json
import os
import re
import requests
import toml
from typing import Any, Dict, cast

from cookiecutter.main import cookiecutter

import seaplane.run_load_dotenv as denv
from seaplane.sdk_internal_utils.http import headers


PROJECT_TOML = "pyproject.toml"


class CliError(Exception):
    pass


def get_project() -> Dict[str, Any]:
    """
    throws an error if the project directory isn't structured in ways
    we expect it to be.
    """
    if not os.path.exists(PROJECT_TOML):
        raise CliError(
            f"{PROJECT_TOML} file missing, run seaplane init"
            " (or change directory to the root of your Seaplane project)"
        )

    project = toml.loads(open(PROJECT_TOML, "r").read())
    project_name = project["tool"]["poetry"]["name"]
    main = project["tool"]["seaplane"].get("main", None)

    if not os.path.exists(project_name):
        raise CliError(
            f"source file {project_name} directory missing, \
                the source code has to live under {project_name} directory."
        )

    if not project_name or not main:
        raise CliError(f"{PROJECT_TOML} not a valid Seaplane project.")

    return project


def cli_deploy() -> None:
    """
    Deploys an app
    """
    project = get_project()
    project_name = project["tool"]["poetry"]["name"]
    main_script = project["tool"]["seaplane"]["main"]
    os.system(f"poetry run python {project_name}/{main_script} deploy")


def cli_destroy() -> None:
    """
    Destroys an app (deletes streams and flows)
    """
    project = get_project()
    project_name = project["tool"]["poetry"]["name"]
    main_script = project["tool"]["seaplane"]["main"]
    os.system(f"poetry run python {project_name}/{main_script} destroy")


def cli_status(watch: bool) -> None:
    """
    Provides status of an app's resources.
      If watch is enabled it must be in your path.
    """
    project = get_project()
    project_name = project["tool"]["poetry"]["name"]
    main_script = project["tool"]["seaplane"]["main"]
    if watch:
        os.system(f"watch poetry run python {project_name}/{main_script} status")
    else:
        os.system(f"poetry run python {project_name}/{main_script} status")


def get_token(fd_url: str) -> str:
    """
    Gets a token from Flightdeck
    """
    # Try to get the API key from .env
    api_key = os.environ.get("SEAPLANE_API_KEY", "None")
    if denv.loaded is False or api_key == "None":
        raise CliError("Set your API key in .env")

    response = requests.post(fd_url, json={}, headers=headers(api_key))
    if response.ok:
        payload = cast(Dict[str, str], response.json())
    else:
        error_body = response.text
        raise CliError(f"Bad Access token request code {response.status_code}, error {error_body}")

    return payload["token"]


def cli_request(data: str) -> None:
    """
    Performs an endpoint request, writes and prints the request_id
    """
    if data[0] == "@":
        try:
            data_bytes = open(data[1:], "rb").read()
        except Exception:
            raise CliError("Cannot load data file.")
    else:
        data_bytes = data.encode()

    # Load schema file
    try:
        schema_file = open(os.path.join("build", "schema.json"), "r")
        schema = json.load(schema_file)
    except Exception:
        raise CliError(
            "Cannot load build schema. Try moving to the directory where you deploy your app."
        )

    # Get a token
    fd_url = schema["identity_endpoint"] + "/token"
    token = get_token(fd_url)

    # Make the request
    for app in schema["apps"]:
        app_id = schema["apps"][app]["id"]
    carrier_endpoint = schema["carrier_endpoint"]
    url = f"{carrier_endpoint}/endpoints/{app_id}/request"
    bearer = {"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"}
    resp = requests.post(url, headers=bearer, data=data_bytes)

    # Empty response handling
    if not resp.content:
        raise CliError(f"Error: empty response from endpoint (code={resp.status_code})")

    # Invalid response format handling
    try:
        resp_content = json.loads(resp.content)
    except json.decoder.JSONDecodeError:
        raise CliError(
            f"Error: invalid JSON response from endpoint (code={resp.status_code}): {resp.content!r}"  # noqa: E501
        )

    # Unexpected response code handling
    if resp.status_code < 200 or resp.status_code >= 300:
        raise CliError(
            f"Error: unexpected response code {resp.status_code} from endpoint: {resp.content!r}"
        )

    # Malformed response handling
    if "request_id" not in resp_content:
        raise CliError(
            f"Error: invalid response from endpoint, missing request_id (code={resp.status_code})"
        )

    request_id = resp_content["request_id"]

    # save the request_id to a file
    with open(".request_id", "a") as f:
        f.write(f"{request_id}\n")
    print(f"\nrequest_id: {request_id}")


def cli_response(request_id: str) -> None:
    """
    Gets an archive response from the endpoint
    """
    # TODO: Could (with arg?) show a list of the last 5-10 ids to choose
    if request_id == "":
        try:
            with open(".request_id", "r") as f:
                request_id = f.readlines()[-1].strip("\n")
        except Exception:
            print("No request_id provided as argument or in file")

    # Load schema file
    try:
        schema_file = open(os.path.join("build", "schema.json"), "r")
        schema = json.load(schema_file)
    except Exception:
        raise CliError(
            "Cannot load build schema. Try moving to the directory where you deploy your app."
        )

    # Get a token
    fd_url = schema["identity_endpoint"] + "/token"
    token = get_token(fd_url)

    # Make the request
    for app in schema["apps"]:
        app_id = schema["apps"][app]["id"]
    carrier_endpoint = schema["carrier_endpoint"]
    url = f"{carrier_endpoint}/endpoints/{app_id}/response/{request_id}/archive"
    bearer = {"Authorization": f"Bearer {token}", "accept": "application/octet-stream"}
    resp = requests.get(url, headers=bearer, params={"pattern": ".>", "format": "json_array"})
    print(f"\nResponse archive for request_id {request_id}:")
    print(resp.content)


def init(project_name: str) -> None:
    """
    Initializes a project using a template
    """
    cookiecutter_template = "https://github.com/seaplane-io/seaplane-app-python-template.git"
    project_directory = "."

    if not project_name.isidentifier():
        suggestion = re.sub("[^A-Za-z0-9_]", "", project_name)
        raise CliError(f'can\'t make a new project named "{project_name}". Try "{suggestion}"')

    extra_context = {"project_slug": project_name, "seaplane_version": version("seaplane")}

    cookiecutter(
        cookiecutter_template,
        output_dir=project_directory,
        no_input=True,  # Disable any interactive prompts
        extra_context=extra_context,
    )

    print(f"🛩️  {project_name} project generated successfully!")


def main() -> None:
    parser = ArgumentParser(prog="seaplane", description="Seaplane Apps command line interface")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Deploy command
    subparsers.add_parser("deploy", help="Deploy command")

    # Destroy command
    subparsers.add_parser("destroy", help="Remove your App and associated tasks")

    # Init command
    init_parser = subparsers.add_parser("init", help="Init command")
    init_parser.add_argument("app", help="Seaplane Apps name")

    # Status command
    stat_parser = subparsers.add_parser("status", help="Status of your app and resources")
    stat_parser.add_argument(
        "--watch",
        "-w",
        default=False,
        action="store_true",
        help="Use UNIX watch command to refresh status every 2s",
    )

    # Endpoints commands
    req_parser = subparsers.add_parser("request", help="Send data to the request endpoint")
    req_parser.add_argument(
        "--data", "-d", type=str, help="Request body, @ to load a file, @- for stdin"
    )
    resp_parser = subparsers.add_parser("response", help="Get data from the response endpoint")
    resp_parser.add_argument("--request_id", "-r", type=str, help="Request ID")

    # Version argument
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=version("seaplane")),
    )

    args = parser.parse_args()

    try:
        if args.command == "deploy":
            cli_deploy()

        elif args.command == "destroy":
            cli_destroy()

        elif args.command == "init":
            init(args.app)

        elif args.command == "status":
            cli_status(args.watch)

        elif args.command == "request":
            if args.data is None:
                raise CliError("Error: expected --data argument to be provided")

            cli_request(args.data)

        elif args.command == "response":
            request_id = ""
            if args.request_id:
                request_id = args.request_id
            cli_response(request_id)

        else:
            parser.print_help()

    except CliError as e:
        print(e)
        exit(1)

    exit(0)


if __name__ == "__main__":
    main()
