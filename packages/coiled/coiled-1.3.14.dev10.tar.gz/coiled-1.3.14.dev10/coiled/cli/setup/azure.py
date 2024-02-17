import json
import shlex
import shutil
import subprocess
import sys
from typing import Optional

import click
from rich import print
from rich.markup import escape
from rich.panel import Panel

import coiled

from ...auth import get_local_user
from ..utils import CONTEXT_SETTINGS
from .util import setup_failure

try:
    from azure.identity import DefaultAzureCredential  # type: ignore
    from azure.mgmt.resource import ResourceManagementClient  # type: ignore
    from azure.mgmt.subscription import SubscriptionClient  # type: ignore

    AZURE_DEPS = True
except ImportError:
    AZURE_DEPS = False


RG_ROLE_NAME = "Coiled Resource Group Role"
LOG_ROLE_NAME = "Coiled Log Access"


def rg_role_def(sub_id):
    return f"""{{
  "Name": "{RG_ROLE_NAME}",
  "IsCustom": true,
  "Description": "Setup and ongoing Coiled permissions required at resource group scope",
  "Actions": [
    "Microsoft.Compute/*/read",
    "Microsoft.Compute/virtualMachines/delete",
    "Microsoft.Compute/virtualMachineScaleSets/*",
    "Microsoft.Network/*/read",
    "Microsoft.Network/applicationSecurityGroups/*",
    "Microsoft.Network/networkSecurityGroups/*",
    "Microsoft.Network/publicIPAddresses/delete",
    "Microsoft.Network/publicIPAddresses/write",
    "Microsoft.Network/virtualNetworks/subnets/join/action",
    "Microsoft.Network/virtualNetworks/subnets/write",
    "Microsoft.Network/virtualNetworks/write",
    "Microsoft.Storage/storageAccounts/managementPolicies/write",
    "Microsoft.Storage/storageAccounts/write"
  ],
  "NotActions": [

  ],
  "AssignableScopes": [
    "/subscriptions/{sub_id}"
  ]
}}"""


def log_role_def(sub_id):
    return f"""{{
  "Name": "{LOG_ROLE_NAME}",
  "IsCustom": true,
  "Description": "Role needs resource group scope for setup, then storage account scope for on-going",
  "Actions": [
    "Microsoft.Storage/storageAccounts/read",
    "Microsoft.Storage/storageAccounts/listkeys/action"
  ],
  "NotActions": [

  ],
  "AssignableScopes": [
    "/subscriptions/{sub_id}"
  ]
}}"""


@click.option(
    "--subscription",
    default=None,
)
@click.option(
    "--resource-group",
    default=None,
)
@click.option(
    "--region",
    default=None,
)
@click.option(
    "--account",
    default=None,
    help="Coiled account that will be configured. By default, uses your default Coiled account.",
)
@click.option(
    "--iam-user",
    default=None,
)
@click.command(context_settings=CONTEXT_SETTINGS)
def azure_setup(subscription, resource_group, region, account, iam_user):
    print("[red]Coiled on Azure is currently in beta, we strongly recommend that you contact us before using.")
    local_user = get_local_user()

    with coiled.Cloud() as cloud:
        coiled_account = account or cloud.default_account

    coiled.add_interaction(
        action="CliSetupAzure",
        success=True,
        local_user=local_user,
        # use keys that match the cli args
        region=region,
    )

    if not AZURE_DEPS:
        print(
            "Required Azure Python libraries are not installed. "
            "You can install with [green]pip install 'coiled\\[azure]'[/green]"
        )
        return

    creds = DefaultAzureCredential()

    sub_id = subscription or get_subscription(creds)

    if not sub_id:
        return

    rg_name, rg_location, rg_id = get_rg(creds, sub_id, rg_name=resource_group or "")
    region = region or rg_location

    if not rg_id:
        return

    print(
        f"Coiled account [green]{coiled_account}[/green] will be configured to use "
        f"resource group [green]{rg_name}[/green] "
        f"with [green]{region}[/green] as the default region"
    )

    app_name = iam_user or f"coiled-{coiled_account}-app"

    print(f"  [bright_black]Creating enterprise application {app_name}...")
    app_json = az_cli_wrapper(f"az ad app create --display-name '{app_name}'")

    app_info = json.loads(app_json)
    app_id = app_info["appId"]

    print(f"  [bright_black]Resetting/retrieving credentials for {app_name} ({app_id})...")
    app_creds_json = az_cli_wrapper(f"az ad app credential reset --id {app_id}")
    app_creds = json.loads(app_creds_json)

    print(f"  [bright_black]Creating service principal for {app_name} ({app_id})...")
    sp_id = strip_output(
        az_cli_wrapper(
            f"az ad sp create --id {app_id} --query id",
            command_if_exists=f"az ad sp list --display-name '{app_name}' --query '[0].id'",
        )
    )

    print(f"  [bright_black]Creating/updating role definition {RG_ROLE_NAME}...")
    az_cli_wrapper(
        f"az role definition create --role-definition '{rg_role_def(sub_id)}'",
        command_if_exists=f"az role definition update --role-definition '{rg_role_def(sub_id)}'",
    )
    print(f"  [bright_black]Creating/updating role definition {LOG_ROLE_NAME}...")
    az_cli_wrapper(
        f"az role definition create --role-definition '{log_role_def(sub_id)}'",
        command_if_exists=f"az role definition update --role-definition '{log_role_def(sub_id)}'",
    )

    print(f"  [bright_black]Assigning '{RG_ROLE_NAME}' role to service principal on '{rg_name}' resource group...")
    az_cli_wrapper(f"az role assignment create --role '{RG_ROLE_NAME}' --scope {rg_id} --assignee {sp_id}")
    print(f"  [bright_black]Assigning '{LOG_ROLE_NAME}' role to service principal on '{rg_name}' resource group...")
    az_cli_wrapper(f"az role assignment create --role '{LOG_ROLE_NAME}' --scope {rg_id} --assignee {sp_id}")

    with coiled.Cloud() as cloud:
        setup_endpoint = f"/api/v2/cloud-credentials/{coiled_account}/azure"
        setup_data = {
            "credentials": {
                "tenant_id": app_creds["tenant"],
                "client_id": app_creds["appId"],
                "client_secret": app_creds["password"],
            },
            "subscription_id": sub_id,
            "resource_group_name": rg_name,
            "default_region": region,
        }
        print("Sending Azure credentials to Coiled...")
        cloud._sync_request(setup_endpoint, method="POST", json=setup_data)

        print("Coiled Azure credentials...")
        # did it work?
        print(cloud._sync_request(setup_endpoint))


def strip_output(output: str) -> str:
    return output.strip(' \n"')


def get_cli_path() -> Optional[str]:
    return shutil.which("az")


def az_cli_wrapper(
    command: str,
    command_if_exists: str = "",
    show_stdout: bool = False,
    interactive: bool = False,
):
    split_command = shlex.split(command)
    if split_command and split_command[0] == "az":
        del split_command[0]
    az_path = get_cli_path() or "az"
    split_command = [az_path] + split_command
    p = subprocess.run(split_command, capture_output=not interactive)

    stdout = p.stdout.decode(encoding=coiled.utils.get_encoding()) if p.stdout else None
    stderr = p.stderr.decode(encoding=coiled.utils.get_encoding(stderr=True)) if p.stderr else None

    if show_stdout:
        print(stdout)

    if not interactive and p.returncode:
        if stderr and "already" in stderr:
            if command_if_exists:
                return az_cli_wrapper(command_if_exists)

            # TODO is this always fine to ignore because it means item exists?
            return ""

        else:
            print(f"[red]az returned an error when running command `{shlex.join(split_command)}`:")
            print(Panel(escape(stderr or "")))
            setup_failure(f"az error while running {shlex.join(split_command)}, {stderr}", backend="azure")
            sys.exit(1)

    return stdout or ""


def get_subscription(credentials):
    sub_client = SubscriptionClient(credentials)

    subscriptions = [
        (subscription.display_name, subscription.subscription_id) for subscription in sub_client.subscriptions.list()
    ]

    if not subscriptions:
        print("No Azure subscriptions were found")
        return None
    elif len(subscriptions) > 1:
        print("Multiple Azure subscriptions were found. Please specify using [green]--subscription <id>[/green]:")
        for name, id in subscriptions:
            print(f"  {name} (id [green]{id}[/green])")
        return None
    else:
        sub_name, sub_id = subscriptions[0]

    return sub_id


def get_rg(credentials, sub_id: str, rg_name: str):
    resource_client = ResourceManagementClient(credentials, sub_id)

    resource_groups = [(rg.name, rg.location, rg.id) for rg in resource_client.resource_groups.list()]

    if not resource_groups:
        print("No Azure resource groups found")
        return None, None, None
    elif len(resource_groups) > 1:
        if rg_name:
            match = [rg for rg in resource_groups if rg[0] and rg[0].lower() == rg_name.lower()]
            if match:
                return match[0]
            else:
                print(f"No resource group matches [green]{rg_name}")

        print("Multiple Azure resource groups found. Please specify using [green]--resource-group <name>[/green]:")
        for name, location, _ in resource_groups:
            print(f"  {name} ({location})")
        return None, None, None
    else:
        return resource_groups[0]
