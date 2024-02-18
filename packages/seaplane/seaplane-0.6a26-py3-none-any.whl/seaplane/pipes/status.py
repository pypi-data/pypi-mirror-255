import json
import os
import requests
from tabulate import tabulate
from typing import List

from seaplane.config import config
from seaplane.errors import SeaplaneError
from seaplane.logs import log
from seaplane.sdk_internal_utils.http import headers
from seaplane.sdk_internal_utils.token_auth import with_token

ENDPOINTS_STREAM = "_SEAPLANE_ENDPOINT"


@with_token
def get_messages(token: str, subject: str) -> str:
    """
    Returns a string with the number of messages in stream subject
      OR "Stream not found" if it does not exist
      OR "0" if the stream exists but subject does not
    """
    stream_name = subject.split(".")[0]
    url = f"{config.carrier_endpoint}/stream/{stream_name}"

    resp = requests.get(
        url,
        headers=headers(token),
    )
    if resp.status_code == 404:
        return "Stream not found"

    stream_info = json.loads(resp.content)
    if stream_info.get("details") is not None:
        if subject in stream_info["details"]["subjects"].keys():
            return str(stream_info["details"]["subjects"][subject])
    return "0"


@with_token
def get_status(token: str, flow_name: str) -> str:
    """
    Returns the status of a flow
      OR "N/A" if status not available
    """
    url = f"{config.carrier_endpoint}/flow/{flow_name}/status"
    if config.dc_region is not None:
        url += f"?region={config.dc_region}"
    resp = requests.get(
        url,
        headers=headers(token),
    )
    if resp.status_code == 200:
        status = json.loads(resp.content)
        replicas = 1
        dead = 0
        output: List[str] = []
        for alloc in status.keys():
            if status[alloc] != "dead":
                output.append(f"{replicas}: {status[alloc]}")
                # We could instead show the alloc id, but it gets busy...
                # output.append(f"{alloc}: {status[alloc]}")
                replicas += 1
            else:
                dead += 1
        if dead > 0:
            output.append(f"{dead} completed tasks")
        return "\n".join(output)
    return "N/A"


@with_token
def status(token: str) -> None:
    """
    Prints the status of resources associated with an app
    """
    try:
        schema_file = open(os.path.join("build", "schema.json"), "r")
        schema = json.load(schema_file)
    except Exception:
        raise SeaplaneError(
            "Cannot load build schema. Try moving to the directory where you deploy your app."
        )

    table_headers = ["Task Name", "Status", "Messages In", "Messages Out"]

    for app in schema["apps"]:
        table = []

        for task in schema["apps"][app]["tasks"]:
            flow_name = task["id"]

            flow_status = get_status(flow_name)

            url = f"{config.carrier_endpoint}/flow/{flow_name}"
            if config.dc_region is not None:
                url += f"?region={config.dc_region}"
            resp = requests.get(
                url,
                headers=headers(token),
            )
            flow_info = json.loads(resp.content)
            log.logger.debug(json.dumps(flow_info, indent=2))

            messages_in = "N/A"
            messages_out = "N/A"
            if "input" in flow_info.keys():
                for source in flow_info["input"]["broker"]:
                    input_subject = source["carrier"]["subject"]
                    messages_in = get_messages(input_subject)
                    # Look at the second switched output for carrier

                output_subject = flow_info["output"]["switch"]["cases"][1]["output"]["carrier"][
                    "subject"
                ]
                messages_out = get_messages(output_subject)

            table.append([flow_name, flow_status, messages_in, messages_out])

        print("\n")
        # "fancy_grid" handles newlines better than "outline"
        print(tabulate(table, table_headers, tablefmt="fancy_grid"))

    print("NOTE: Message counts are currently unavailable for HTTP ENDPOINTS.")
