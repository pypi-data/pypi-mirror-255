from typing import Optional

import click

import coiled

from ..utils import CONTEXT_SETTINGS
from .utils import find_cluster


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("cluster", default="", required=False)
@click.option(
    "--account",
    default=None,
    help="Coiled account (uses default account if not specified)",
)
def stop(
    cluster: str,
    account: Optional[str],
):
    with coiled.Cloud(account=account) as cloud:
        cluster_info = find_cluster(cloud, cluster)
        cluster_id = cluster_info["id"]
        cloud.delete_cluster(cluster_id, account, reason="User requsted stop via CLI")
