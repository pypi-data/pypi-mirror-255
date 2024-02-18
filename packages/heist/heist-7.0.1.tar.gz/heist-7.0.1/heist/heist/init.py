"""
The entry point for Heist, this is where config loading and the project
spine is set up
"""
import asyncio
import ipaddress
import pathlib
import socket
import subprocess
import sys
from typing import Any

from dict_tools.data import NamespaceDict


def __init__(hub):
    hub.heist.CONS = {}
    hub.heist.ROSTERS = {}

    # Load all relative subs onto the hub recursively
    hub.pop.sub.load_subdirs(hub.heist, recurse=True)
    for dyne in ("artifact", "rend", "roster", "service", "tunnel", "tool", "output"):
        hub.pop.sub.add(dyne_name=dyne)
    hub.pop.sub.load_subdirs(hub.service, recurse=True)


def cli(hub):
    """
    Load the cli as the first thing we do to account for pluggable OS dependent systems.
    """
    hub.pop.config.load(["heist", "rend"], cli="heist")
    hub.heist.init.env()

    # Create a path on host system to cache downloads
    # This location is where grains and salt binary will be downloaded to
    pathlib.Path(hub.OPT.heist.artifacts_dir).mkdir(0o700, parents=True, exist_ok=True)
    if sys.platform.startswith("win"):
        subprocess.run(["icacls", hub.OPT.heist.artifacts_dir, "inheritance:d"])
        subprocess.run(
            ["icacls", hub.OPT.heist.artifacts_dir, "/remove", "Users", "/T"]
        )
        subprocess.run(["icacls", hub.OPT.heist.artifacts_dir, "/GRANT:R", "Users:(R)"])

    # If we are on windows, create a separate loop so we can handle the
    # keyboard interrupt. due to issues with current asyncio, windows, and
    # python together, we cannot support signals natively when running from
    # windows. therefore, we must diverge code here
    if "win" in sys.platform:
        hub.pop.loop.create()
        try:
            hub.pop.Loop.run_until_complete(hub.heist.init.start_win())
        except KeyboardInterrupt:
            hub.log.debug("Caught keyboard interrupt")
        finally:
            hub.pop.Loop.run_until_complete(hub.heist.init.clean())
            hub.pop.Loop.close()
    else:
        hub.heist.init.start_nix()


def env(hub):
    """
    Translate the config into the needed vars on the hub.
    :param hub:
    :return:
    """
    if hub.OPT["heist"].run_dir_root:
        run_dir_root = hub.OPT["heist"].run_dir_root
        hub.heist.OS_DEFAULTS = {
            "linux": {
                "os_path": "/var/tmp/heist",
                "user": "root",
                "run_dir_root": run_dir_root,
            },
            "windows": {
                "os_path": "C:\\Windows\\temp\\heist",
                "user": "Administrator",
                "run_dir_root": run_dir_root,
            },
            "default": {
                "os_path": "/var/tmp/heist",
                "user": "root",
                "run_dir_root": run_dir_root,
            },
        }
    else:
        hub.heist.OS_DEFAULTS = {
            "linux": {
                "os_path": "/var/tmp/heist",
                "user": "root",
                "run_dir_root": "/var/tmp/",
            },
            "windows": {
                "os_path": "C:\\Windows\\temp\\heist",
                "user": "Administrator",
                "run_dir_root": "C:\\Windows\\temp\\",
            },
            "default": {
                "os_path": "/var/tmp/heist",
                "user": "root",
                "run_dir_root": "/var/tmp/",
            },
        }


def default(hub, target_os: str, key: str) -> Any:
    os_defaults = hub.heist.OS_DEFAULTS.get(target_os)
    if not os_defaults:
        value = None
        hub.log.error(f"OS '{target_os}' not defined in hub.heist.OS_DEFAULTS")
    else:
        value = os_defaults.get(key)

    if not value:
        hub.log.error(f"No {target_os}-specific default for {key}, using fallback")
        value = hub.heist.OS_DEFAULTS["default"].get(key)

    return value


def start_nix(hub):
    """
    Start the async loop and get the process rolling for linux based systems
    """
    if not hub.SUBPARSER:
        hub.log.critical("Must set a heist manager")
        return False

    try:
        hub.pop.loop.start(
            hub.heist.init.run_remotes(
                hub.SUBPARSER,
                artifact_version=hub.OPT.heist.artifact_version,
                roster_file=hub.OPT.heist.roster_file,
                roster=hub.OPT.heist.roster,
                roster_data=hub.OPT.heist.roster_data,
                manage_service=hub.OPT.heist.manage_service,
                clean=hub.OPT.heist.clean,
            ),
            sigint=hub.heist.init.clean,
            sigterm=hub.heist.init.clean,
        )
    except asyncio.CancelledError:
        hub.log.debug("Cancelled remaining running asyncio tasks")
    finally:
        hub.pop.Loop.close()


async def start_win(hub):
    """
    Start the async loop and get the process rolling for nt based systems
    """
    if not hub.SUBPARSER:
        hub.log.critical("Must set a heist manager")
        return False

    await hub.heist.init.run_remotes(
        hub.SUBPARSER,
        artifact_version=hub.OPT.heist.artifact_version,
        roster_file=hub.OPT.heist.roster_file,
        roster=hub.OPT.heist.roster,
        roster_data=hub.OPT.heist.roster_data,
        manage_service=hub.OPT.heist.manage_service,
        clean=hub.OPT.heist.clean,
    )


def display_output(hub, out):
    """
    print results to the screen
    for the user
    """
    lines = []
    for target in out:
        for key, value in target.items():
            if target["retvalue"] == 0:
                # print green
                lines.append(f"\033[92m {key}: {value}\033[00m\n")
            else:
                # print red
                lines.append(f"\033[91m {key}: {value}\033[00m\n")
    print("".join(lines))


async def run_remotes(
    hub,
    manager: str,
    artifact_version=None,
    roster_file: str = "",
    roster: str = None,
    roster_data=None,
    manage_service=None,
    clean=False,
    **kwargs,
):
    """
    Configs, rosters and targets have been loaded, time to execute the
    remote system calls
    """
    try:
        raw_remotes = await hub.roster.init.read(
            roster, roster_file=roster_file, roster_data=roster_data
        )
    except ValueError as err:
        hub.log.error(err.args[0])
        return False
    remotes = NamespaceDict()
    for k, v in raw_remotes.items():
        remotes[k] = NamespaceDict(v)
    if not remotes:
        return False

    hub.log.debug(f"Heist manager is '{manager}'")

    if manage_service:
        valid_opts = ["start", "restart", "stop", "enable", "disable", "status"]
        if manage_service not in valid_opts:
            hub.log.error(f"The service cannot be managed with {manage_service}")
            hub.log.error(f"Please use one of {valid_opts}")
            return False
    ret = hub.heist[manager].run(
        remotes,
        artifact_version=artifact_version,
        manage_service=manage_service,
        clean=clean,
        **kwargs,
    )
    if asyncio.iscoroutine(ret):
        _ret = await ret

    hub.heist.init.display_output(out=_ret)
    return _ret


async def clean(hub, signal: int = None):
    """
    Clean up the connections
    """
    if signal:
        hub.log.warning(f"Got signal {signal}! Cleaning up connections")
    coros = []
    # First clean up the remote systems
    if hub.OPT.heist.noclean:
        hub.log.info("`noclean` was set. Will not clean up the minion")
    else:
        for target_name, r_vals in hub.heist.ROSTERS.items():
            if not r_vals.get("bootstrap"):
                vals = hub.heist.CONS[target_name]
                manager = vals["manager"]
                coros.append(
                    hub.heist[manager].clean(
                        target_name,
                        vals["tunnel_plugin"],
                        service_plugin=vals.get("service_plugin"),
                        vals=vals,
                    )
                )
        await asyncio.gather(*coros)
    # Then shut down connections
    coros = []
    for target_name, vals in hub.heist.CONS.items():
        tunnel_plugin = vals["tunnel_plugin"]
        coros.append(hub.tunnel[tunnel_plugin].destroy(target_name))
    await asyncio.gather(*coros)
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()


def ip_is_loopback(hub, addr):
    """
    helper function to determine if an addr
    or hostname is a loopback address
    """
    try:
        info = socket.getaddrinfo(addr, 0)
    except socket.gaierror:
        hub.log.critical("Could not determine if addr is loopback")
        return False
    return ipaddress.ip_address(info[0][-1][0]).is_loopback
