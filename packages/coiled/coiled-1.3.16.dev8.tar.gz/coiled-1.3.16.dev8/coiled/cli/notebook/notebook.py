from __future__ import annotations

import asyncio
import os
import shlex
import shutil
import signal
import subprocess
from typing import Optional, Sequence, Tuple, Union
from webbrowser import open as open_webbrowser

import click
import importlib_metadata
from packaging.version import Version
from rich import print
from rich.console import Console
from rich.control import Control
from rich.prompt import Confirm
from rich.segment import ControlType
from urllib3.util import parse_url

import coiled
from coiled.cli.cluster.ssh import add_key_to_agent, check_ssh_agent, get_ssh_add_path, get_ssh_path
from coiled.compatibility import DISTRIBUTED_VERSION
from coiled.errors import DoesNotExist
from coiled.utils import error_info_for_tracking

from ...utils import unset_single_thread_defaults
from ...v2.widgets.rich import LightRichClusterWidget
from ..utils import CONTEXT_SETTINGS

# Path on VM to sync to.
# We use `/scratch` for now because it's already bind-mounted into docker.
SYNC_TARGET = "/scratch/synced"
MIN_DISTRIBUTED_VERSION = Version("2022.8.1")
MUTAGEN_NAME_FORMAT = "coiled-{cluster_id}"


class NotebookError(Exception):
    pass


def check_distributed_version() -> bool:
    if DISTRIBUTED_VERSION < MIN_DISTRIBUTED_VERSION:
        print(
            "[bold red]"
            f"distributed>{MIN_DISTRIBUTED_VERSION} is required to launch notebooks. "
            f"You have {DISTRIBUTED_VERSION}."
            "[/]"
        )
        return False
    return True


def check_jupyter() -> bool:
    try:
        importlib_metadata.distribution("jupyterlab")
    except ModuleNotFoundError:
        print("[bold red]Jupyterlab must be installed locally to launch notebooks.[/]")
        return False

    try:
        importlib_metadata.distribution("jupyter_server_proxy")
    except ModuleNotFoundError:
        print(
            "[bold red]jupyter-server-proxy is not installed, "
            "without this you won't be able to access Dask dashboard for local clusters created on notebook server.[/]"
        )

    return True


def get_mutagen_path() -> Optional[str]:
    mutagen_path = shutil.which("mutagen")
    if not mutagen_path:
        print(
            "[bold red]"
            "mutagen must be installed to synchronize files with notebooks.[/]\n"
            "Install via homebrew (on macOS, Linux, or Windows) with:\n\n"
            "brew install mutagen-io/mutagen/mutagen@0.16\n\n"
            "Or, visit https://github.com/mutagen-io/mutagen/releases/latest to download "
            "a static, pre-compiled binary for your system, and place it anywhere on your $PATH."
        )
        return None
    return mutagen_path


def get_ssh_keygen_path() -> Optional[str]:
    ssh_keygen_path = shutil.which("ssh-keygen")
    if not ssh_keygen_path:
        print("[bold red]Unable to find `ssh-keygen`, you may need to install OpenSSH or add it to your paths.[/]")
        return None
    return ssh_keygen_path


def mutagen_session_exists(cluster_id: int) -> bool:
    mutagen_path = get_mutagen_path()
    if not mutagen_path:
        return False
    sessions = (
        subprocess.run(
            [
                mutagen_path,
                "sync",
                "list",
                "--label-selector",
                f"managed-by=coiled,cluster-id={cluster_id}",
                "--template",
                "{{range .}}{{.Name}}{{end}}",
            ],
            text=True,
            capture_output=True,
        )
        .stdout.strip()
        .splitlines()
    )

    if not sessions:
        return False
    if sessions == [MUTAGEN_NAME_FORMAT.format(cluster_id=cluster_id)]:
        return True

    if len(sessions) == 1:
        raise RuntimeError(
            f"Unexpected mutagen session name {sessions[0]!r}. "
            f"Expected {MUTAGEN_NAME_FORMAT.format(cluster_id=cluster_id)!r}."
        )

    raise RuntimeError(f"Multiple mutagen sessions found for cluster {cluster_id}: {sessions}")


def add_host_to_known_hosts(console, target: str) -> Tuple[bool, str]:
    # Since we may not know the location of known_hosts, use `ssh` to add the key to the agent
    ssh_path = get_ssh_path()
    if not ssh_path:
        raise RuntimeError("ssh not installed")
    result = subprocess.run(
        [
            ssh_path,
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=5",
            "-o",
            "StrictHostKeyChecking=no",
            target,
            "echo",
            "ok",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        console.print(f"[red]Error attempting to ssh...[/red]\n\n{result.stderr}")
        return False, result.stderr
    return True, ""


def connect_mutagen_sync(cloud, cluster_id, console, include_vcs: bool = False, debug=False) -> Tuple[bool, str]:
    if mutagen_session_exists(cluster_id):
        console.print("[bold]File sync session already active; reusing it.[/]")
    else:
        console.print("[bold]Launching file synchronization...[/]")
        ssh_info = cloud.get_ssh_key(cluster_id)

        scheduler_address = ssh_info["scheduler_hostname"] or ssh_info["scheduler_public_address"]
        target = f"ubuntu@{scheduler_address}"

        add_key_to_agent(scheduler_address, key=ssh_info["private_key"])

        added, ssh_error = add_host_to_known_hosts(console, target)
        if not added:
            return False, ssh_error

        if debug:
            ssh_keygen = shutil.which("ssh-keygen")
            if ssh_keygen:
                proc = subprocess.run(
                    [ssh_keygen, "-H", "-F", scheduler_address],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                console.print(f"Existing known_hosts entries for {scheduler_address}:\n[green]{proc.stdout}[/green]\n")
            ssh_add_path = get_ssh_add_path()
            if ssh_add_path:
                proc = subprocess.run(
                    [ssh_add_path, "-l"],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                console.print(f"Existing ssh keys:\n[green]{proc.stdout}[/green]\n")

        # Start mutagen
        sync_command = [
            "mutagen",
            "sync",
            "create",
            "--name",
            MUTAGEN_NAME_FORMAT.format(cluster_id=cluster_id),
            "--label",
            "managed-by=coiled",
            "--label",
            f"cluster-id={cluster_id}",
            "--no-ignore-vcs" if include_vcs else "--ignore-vcs",
            "--max-staging-file-size=1 GiB",
            # make files on the remote public (to avoid problems if uid on host != uid in container)
            "--default-file-mode-beta=666",
            "--default-directory-mode-beta=0777",
            ".",
            f"{target}:{SYNC_TARGET}",
        ]
        if debug:
            console.print(f"Sync command:\n[green]{shlex.join(sync_command)}[/green]\n")

        result = subprocess.run(
            sync_command,
            check=False,
            text=True,
            capture_output=True,
        )

        # TODO show output live by wrapping console.print as file object that we pass to subprocess.run (?)
        if result.stderr:
            console.print(f"[red]Error attempting to connect sync...[/red]\n\n{result.stderr}")
        elif result.stdout:
            console.print(result.stdout)

        if result.returncode != 0:
            # there was a problem starting mutagen sync, so no reason to link the sync directory
            # (and most likely ssh is the problem so this too would fail)
            return False, result.stderr

        # From host (outside container), make the directory and set permissions.
        # If container user doesn't match host user, then we can't do this *inside* container.
        outside_dir_setup = f"mkdir -p {SYNC_TARGET} && chmod a+rwx {SYNC_TARGET}"

        # Within the docker container, symlink the sync directory (`/scratch/sync`)
        # into the working directory for Jupyter, so you can actually see the synced
        # files in the Jupyter browser. We use a symlink since the container doesn't
        # have capabilities to make a bind mount.
        # TODO if we don't like the symlink, Coiled could see what the workdir is for
        #  the image before running, and bind-mount `/sync` on the host to `$workdir/sync`
        #  in the container? Custom docker images make this tricky; we can't assume anything
        #  about the directory layout or what the working directory will be.
        inside_dir_setup = f"docker exec tmp-dask-1 bash -c 'ln -s {SYNC_TARGET} .'"

        symlink_command = [
            "ssh",
            target,
            f"{outside_dir_setup} && {inside_dir_setup}",
        ]
        if debug:
            console.print(
                "Symlink command so /sync in notebook maps to synced directory:\n"
                f"[green]{shlex.join(symlink_command)}[/green]\n"
            )
        subprocess.run(
            symlink_command,
            check=True,
            capture_output=True,
        )
    return True, ""


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--name",
    default=None,
    help="Cluster name. If not given, defaults to a hash based on current working directory.",
)
@click.option(
    "--account",
    default=None,
    help="Coiled account (uses default account if not specified)",
)
@click.option(
    "--sync",
    default=False,
    is_flag=True,
    help="Sync the working directory with the filesystem on the notebook. Requires mutagen.",
)
@click.option(
    "--software",
    default=None,
    help=(
        "Software environment name to use. If neither software nor container is specified, "
        "all the currently-installed Python packages are replicated on the VM using package sync."
    ),
)
@click.option(
    "--container",
    default=None,
    help=(
        "Container image to use. If neither software nor container is specified, "
        "all the currently-installed Python packages are replicated on the VM using package sync."
    ),
)
@click.option(
    "--vm-type",
    default=[],
    multiple=True,
    help="VM type to use. Specify multiple times to provide multiple options.",
)
@click.option("--cpu", default=None, type=int, help="Number of CPUs requested for this notebook.")
@click.option(
    "--memory",
    default=None,
    help="Amount of memory for this notebook, Coiled will use a +/-10% buffer from the memory you specify.",
)
@click.option(
    "--gpu",
    default=False,
    is_flag=True,
    help="Use GPU notebook server.",
)
@click.option(
    "--disk-size",
    default=None,
    help="Use larger-than-default disk on VM, specified in GiB.",
)
@click.option(
    "--region",
    default=None,
    help="The cloud provider region in which to run the notebook.",
)
@click.option(
    "--open",
    default=True,
    is_flag=True,
    help="Whether to open the notebook in the default browser once it's launched.",
)
@click.option(
    "--block/--no-block",
    default=True,
    is_flag=True,
    help="Whether to block while the notebook is running.",
)
@click.option(
    "--include-vcs",
    default=False,
    is_flag=True,
    help="Include version control files when syncing (e.g., `.git`).",
)
@click.option(
    "--idle-timeout",
    default="4 hours",
    help="Period of idleness after which to automatically shut down the notebook, "
    "e.g. '20 minutes' or '1 hour' or '10 days' (default is '4 hours'). "
    "The notebook is considered active (not idle) if a browser is connected, "
    "even if no code is running.",
)
def start_notebook(
    name: Optional[str],
    account: Optional[str],
    sync: bool,
    software: Optional[str],
    container: Optional[str],
    vm_type: Sequence[str],
    cpu: Union[int, None],
    memory: Union[str, None],
    gpu: bool,
    disk_size: Optional[int],
    region: Optional[str],
    open: bool,
    block: bool,
    include_vcs: bool,
    idle_timeout: str,
):
    """
    Launch or re-open a notebook session, with optional file syncing.

    If a notebook session with the same ``name`` already exists, it's not re-created.
    If file sync was initially not enabled, running ``coiled notebook start --sync``
    will begin file sync without re-launching the notebook.
    """
    _start_notebook(
        name=name,
        account=account,
        sync=sync,
        software=software,
        container=container,
        vm_type=vm_type,
        cpu=cpu,
        memory=memory,
        gpu=gpu,
        disk_size=disk_size,
        region=region,
        open=open,
        block=block,
        include_vcs=include_vcs,
        idle_timeout=idle_timeout,
    )


def _start_notebook(
    *,
    name: Optional[str] = None,
    account: Optional[str] = None,
    sync: bool = False,
    software: Optional[str] = None,
    container: Optional[str] = None,
    vm_type: Sequence[str] = [],
    cpu: Union[int, None] = None,
    memory: Union[str, None] = None,
    gpu: bool = False,
    disk_size: Optional[int] = None,
    region: Optional[str] = None,
    open: bool = False,
    block: bool = True,
    include_vcs: bool = False,
    idle_timeout: str = "4 hours",
    debug: bool = False,
):
    """
    Launch or re-open a notebook session, with optional file syncing.

    If a notebook session with the same ``name`` already exists, it's not re-created.
    If file sync was initially not enabled, running ``coiled notebook start --sync``
    will begin file sync without re-launching the notebook.
    """
    info = {"vm_type": vm_type, "sync": sync, "block": block, "include_vcs": include_vcs}
    success = True
    exception = None

    try:
        # when using package sync, check that local env has jupyter and recent distributed
        if not software and not container:
            if not check_distributed_version():
                raise NotebookError("distributed version check")
            if not check_jupyter():
                raise NotebookError("jupyter missing")

        mutagen_path = get_mutagen_path()
        if sync and not (mutagen_path and get_ssh_path() and get_ssh_keygen_path()):
            return

        if sync and not check_ssh_agent():
            print("Sync may be unable to start but we'll try anyway...")
            info["problem"] = "check_ssh_agent failed"

        env = unset_single_thread_defaults()
        if container and "rapidsai" in container:
            env["DISABLE_JUPYTER"] = "true"  # needed for "stable" RAPIDS image

        name = name or f"notebook-{coiled.utils.short_random_string()}"
        with LightRichClusterWidget(
            account=account, title=f"Notebook [bold]{name}[/bold]...", jupyter_link="...", width=84
        ) as widget, coiled.Cloud(account=account) as cloud:
            account = account or cloud.default_account
            info["account"] = account
            widget.update(
                server=cloud.server,
                cluster_details=None,
                logs=None,
                account=account,
                jupyter_link="...",
            )
            cluster = coiled.Cluster(
                name=name,
                cloud=cloud,
                n_workers=0,
                software=software,
                container=container,
                jupyter=True,
                scheduler_options={"idle_timeout": idle_timeout},
                scheduler_vm_types=list(vm_type) if vm_type else None,
                worker_vm_types=list(vm_type) if vm_type else None,
                scheduler_cpu=cpu,
                scheduler_memory=memory,
                scheduler_disk_size=disk_size,
                allow_ssh=True,
                environ=env,
                scheduler_gpu=gpu,
                region=region,
                tags={"coiled-cluster-type": "notebook"},
                custom_widget=widget,
            )
            info["cluster_id"] = cluster.cluster_id

            url = cluster.jupyter_link
            cluster_id = cluster.cluster_id
            assert cluster_id is not None

            # by default, jupyter on the scheduler gives us client to that very scheduler
            # clear ENV var so default `Client()` on notebook gives us a new local cluster
            cluster.unset_env_vars(["DASK_SCHEDULER_ADDRESS"])

            if sync:
                url = parse_url(url)._replace(path="/jupyter/lab/tree/synced").url

            widget.update(
                cluster_details=None,
                logs=None,
                jupyter_link=url,
            )

            if sync:
                connected, error_message = connect_mutagen_sync(
                    cloud, cluster_id, widget.live.console, include_vcs=include_vcs, debug=debug
                )
                if not connected:
                    widget.stop()
                    print(
                        "[red]Unable to start sync, see error shown above for more details.[/red]\n"
                        "If sync is not required, you can start notebook without [green]--sync[/green]."
                    )

                    _stop_notebook(name=name, account=account, cluster_id=cluster_id)

                    # close the cluster object so we comms close cleanly (and don't print error)
                    cluster.close(reason="The noteboook sync failed to start")
                    raise NotebookError(f"unable to start sync: {error_message}")

            if open:
                open_webbrowser(url, new=2)

            if block:
                widget.update(
                    cluster_details=None,
                    logs=None,
                    trailer="Use Control-C to stop this notebook server",
                )

                def signal_handler_noop(_, frame):
                    # Ignore the input signal
                    return

                async def update_widget():
                    while True:
                        cluster_details = await cloud._get_cluster_details(cluster_id=cluster_id, account=account)
                        widget.update(cluster_details, logs=None)
                        # don't make user hit control-c if the cluster been stopped another way
                        if cluster_details["scheduler"]["current_state"]["state"] in ("error", "stopped"):
                            return False
                        await asyncio.sleep(1.0)

                while True:
                    try:
                        if not cluster.sync(update_widget):
                            widget.stop()
                            break
                    except KeyboardInterrupt:
                        widget.stop()
                        try:
                            exit = Confirm.ask("Are you sure you want to stop this notebook server?", default=True)
                        except KeyboardInterrupt:
                            exit = True
                        if exit:
                            # Register noop handler since we're shutting down and
                            # want to make sure the notebook is shutdown even when
                            # hammering ctrl-C
                            signal.signal(signal.SIGINT, signal_handler_noop)
                            break
                        else:
                            # write over the prompt
                            print(Control.move(0, -1), Control((ControlType.ERASE_IN_LINE, 2)))
                            print("[green]Continuing with this notebook server... [/]")

                            # move cursor to bottom of widget so widget won't shift
                            print(Control.move(0, -2))
                            widget.start()

                _stop_notebook(name=name, account=account, cluster_id=cluster_id)

                # close the cluster object so we comms close cleanly (and don't print error)
                cluster.close()
            else:
                stop_command = "coiled notebook stop"
                if account:
                    stop_command = f"{stop_command} --account {account}"
                stop_command = f"{stop_command} {name}"

                print(f"To stop this notebook server: [green]{stop_command}[/]")
    except NotebookError as e:
        success = False
        exception = e
        # don't raise, we've already printed appropriate message about the issue
    except Exception as e:
        success = False
        exception = e
        raise e
    finally:
        coiled.add_interaction(
            "coiled-notebook",
            success=success,
            **info,
            **error_info_for_tracking(exception),
        )


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("name")
@click.option(
    "--account",
    default=None,
    help="Coiled account (uses default account if not specified)",
)
def stop_notebook(name: str, account: Optional[str]):
    """
    Shut down a notebook session
    """
    _stop_notebook(name=name, account=account)


def _stop_notebook(name: str, account: Optional[str], cluster_id: Optional[int] = None):
    with coiled.Cloud(account=account) as cloud:
        notebook_running = True
        try:
            cluster_id = cloud.get_cluster_by_name(name)
        except DoesNotExist:
            if cluster_id:
                print(f"[bold red]Notebook {name!r} is already stopped[/]")
            else:
                print(f"[bold red]Notebook {name!r} does not exist[/]")
            notebook_running = False

        mutagen_path = get_mutagen_path()
        if cluster_id and mutagen_path and mutagen_session_exists(cluster_id):
            # NOTE: we can't tell if the user asked for `--sync` or not at creation.
            # Best we can do is check if mutagen is installed and the session exists.
            ssh_keygen_path = get_ssh_keygen_path()
            if not ssh_keygen_path:
                return

            # Stop mutagen
            print(f"Stopping sync with notebook {name!r} ({cluster_id})")
            subprocess.run([mutagen_path, "sync", "terminate", MUTAGEN_NAME_FORMAT.format(cluster_id=cluster_id)])

            ssh_info = cloud.get_ssh_key(cluster_id)
            scheduler_address = ssh_info["scheduler_hostname"] or ssh_info["scheduler_public_address"]
            add_key_to_agent(scheduler_address, key=ssh_info["private_key"], delete=True)

            # Remove `known_hosts` entries.
            # TODO don't like touching the user's `known_hosts` file like this.
            subprocess.run(
                [
                    ssh_keygen_path,
                    "-f",
                    os.path.expanduser("~/.ssh/known_hosts"),
                    "-R",
                    scheduler_address,
                ],
                capture_output=True,
            )

        if cluster_id and notebook_running:
            print(f"Stopping notebook {name!r} ({cluster_id})...")
            cloud.delete_cluster(cluster_id, account, reason="User requested notebook stop via CLI")


@click.command(context_settings=CONTEXT_SETTINGS, hidden=True)
@click.argument("name")
@click.option(
    "--include-vcs",
    default=False,
    is_flag=True,
    help="Include version control files when syncing (e.g., `.git`).",
)
@click.option(
    "--debug",
    default=False,
    is_flag=True,
)
def start_standalone_sync(name: str, include_vcs: bool, debug: bool):
    mutagen_path = get_mutagen_path()
    if not mutagen_path:
        return

    with coiled.Cloud() as cloud:
        try:
            cluster_id = cloud.get_cluster_by_name(name)
        except DoesNotExist:
            print(f"[bold red]Cluster {name!r} does not exist[/]")
            return

        _, error = connect_mutagen_sync(
            cloud=cloud, cluster_id=cluster_id, console=Console(), include_vcs=include_vcs, debug=debug
        )
        if error:
            print(error)

    coiled.add_interaction(
        "coiled-notebook-standalone-sync",
        success=not error,
        include_vcs=include_vcs,
    )


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("name")
def monitor_sync(name: str):
    """Monitor file sync status for a notebook session."""
    mutagen_path = get_mutagen_path()
    if not mutagen_path:
        return

    with coiled.Cloud() as cloud:
        try:
            cluster_id = cloud.get_cluster_by_name(name)
        except DoesNotExist:
            print(f"[bold red]Cluster {name!r} does not exist[/]")
            return  # TODO exit 1

    if not mutagen_session_exists(cluster_id):
        print(f"[bold red]No file synchronization session for cluster {name!r} ({cluster_id})[/]")
        return  # TODO exit 1

    subprocess.run([mutagen_path, "sync", "monitor", MUTAGEN_NAME_FORMAT.format(cluster_id=cluster_id)])
