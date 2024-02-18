import inspect
import re
from typing import Any

import asyncssh
from dict_tools.data import NamespaceDict

__virtualname__ = "asyncssh"


def __init__(hub):
    """
    Set up the objects to hold connection instances
    """
    hub.tunnel.asyncssh.CONS = {}


def _autodetect_asyncssh_opt(hub, option: str) -> Any:
    """"""
    # TODO autodetect certain options
    return None


def _get_asyncssh_opt(hub, target, option: str, default: Any = None) -> Any:
    """
    Get an assyncssh option from the target/roster first, if that fails get it from the config, if not there
    then try to autodetect the option (I.E. Checking for keys in the .ssh folder of the target)
    :param option:
    :param target:
    :return:
    """
    result = target.get(option)
    if not result and "heist" in hub.OPT:
        result = hub.OPT.heist.get(option)
        if not result:
            result = hub.OPT.heist.roster_defaults.get(option)
    if not result:
        result = _autodetect_asyncssh_opt(hub, option)
    if not result:
        result = default
    return result


async def create(hub, name: str, target, reconnect=False):
    """
    Create a connection to the remote system using a dict of values that map
    to this plugin. Name the connection for future use, the connection data
    will be stored on the hub under hub.tunnel.asyncssh.CONS
    :param name:
    :param target:
    """
    if name in hub.tunnel.asyncssh.CONS and not reconnect:
        hub.log.debug(f"tunnel {name} already exists")
        return True

    # The id MUST be in the target, everything else might be in the target, conf, or elsewhere
    target = target.copy()
    id_ = target.pop("host", None) or target["id"]

    possible_options = set(
        inspect.getfullargspec(asyncssh.SSHClientConnectionOptions.prepare).args
    )
    # Remove options from `inspect` that don't belong
    possible_options -= {"self", "args", "kwargs", "tunnel"}
    # Add connection options that aren't specified in `SSHClientConnectionOptions.prepare`
    possible_options.update(
        {"port", "loop", "family", "flags", "local_addr", "options"}
    )
    # Check for each possible SSHClientConnectionOption in the target, config, then autodetect (if necessary)
    con_opts = {"known_hosts": None}
    for arg in possible_options:
        opt = _get_asyncssh_opt(hub, target, arg)
        if opt is not None:
            con_opts[arg] = opt

    try:
        conn = await asyncssh.connect(id_, **con_opts)
    except Exception as e:
        hub.log.error(f"Failed to connect to '{id_}': {e}")
        return False
    sftp = await conn.start_sftp_client()

    hub.tunnel.asyncssh.CONS[name] = {
        "con": conn,
        "sftp": sftp,
        "sudo": target.get("sudo", None),
        "tty": target.get("tty"),
        "term_type": target.get("term_type"),
        "term_size": target.get("term_size"),
        "password": target.get("password"),
    }
    return True


async def send(hub, name: str, source: str, dest: str, preserve=False, recurse=False):
    """
    Take the file located at source and send it to the remote system

    :param name: The name of the asyncssh tunnel connection
    :param source: The full path to the source location.
    :param dest: The full path to the destination location.
    :param preserve: Preserve the permissions on the destination host for
         the files being copied.
    :param recurse: Recursively copy a directory over to the destination
         host
    """
    target = hub.tunnel.asyncssh.CONS[name]
    sftp = target["sftp"]
    if target["sudo"]:
        # TODO run SFTP with permissions
        pass
    await sftp.put(source, dest, preserve=preserve, recurse=recurse)
    return True


async def get(hub, name: str, source: str, dest: str):
    """
    Take the file located on the remote system and copy it locally
    """
    sftp = hub.tunnel.asyncssh.CONS[name]["sftp"]
    await sftp.get(source, dest)


async def cmd(
    hub,
    name: str,
    command: str,
    background=False,
    target_os="linux",
    sudo=None,
    **kwargs,
):
    """
    Execute the given command on the machine associated with the named connection
    """
    # Allow us to bypass sudo settings in roster for commands
    # that do not require sudo via kwargs
    if sudo is None:
        sudo = hub.tunnel.asyncssh.CONS[name].get("sudo")
    sudo_password = re.compile(r"(?:.*)[Pp]assword(?: for .*)?:", re.M)
    con: asyncssh.SSHClientConnection = hub.tunnel.asyncssh.CONS[name]["con"]
    if target_os == "windows":
        win_background_cmd = command
        arg_list = win_background_cmd.split()
        win_background_cmd = arg_list.pop(0)
        arg_list = " ".join(arg_list)
        win_background_cmd = (
            "powershell -command "
            + '"'
            + "; ".join(
                [
                    f"$action = New-ScheduledTaskAction -Execute '{win_background_cmd}' "
                    f"-Argument '{arg_list}'",
                    "$trigger = New-ScheduledTaskTrigger -Once -At 00:00",
                    "$principal = New-ScheduledTaskPrincipal "
                    '-UserId "$env:USERNAME" '
                    '-LogonType "S4U" '
                    "-RunLevel Highest",
                    "Register-ScheduledTask -Action $action "
                    "-Trigger $trigger "
                    "-Principal $principal "
                    "-TaskName heist-background "
                    "-Description 'Run background process' "
                    "-Force",
                    "Start-ScheduledTask -TaskName heist-background",
                    "Unregister-ScheduledTask -TaskName heist-background "
                    "-Confirm:$false",
                ]
            )
            + '"'
        )

    result = {}
    if hub.tunnel.asyncssh.CONS[name].get("tty"):
        kwargs["term_type"] = (
            hub.tunnel.asyncssh.CONS[name].get("term_type") or "xterm-color"
        )
        kwargs["term_size"] = hub.tunnel.asyncssh.CONS[name].get("term_size") or (
            80,
            24,
        )
    if sudo:
        if background:
            if target_os == "windows":
                command = win_background_cmd
            else:
                command = f"sudo -b su -c '{command} &'"
        else:
            if target_os != "windows":
                command = f"sudo {command}"
        async with con.create_process(command, **kwargs) as process:
            while not process.stdout.at_eof():
                output = await process.stdout.read(1024)
                if sudo_password.search(output):
                    process.stdin.write(
                        hub.tunnel.asyncssh.CONS[name].get("password") + "\n"
                    )
                stdout = output
                if not stdout:
                    stdout = await process.stdout.read()
                stderr = await process.stderr.readline()
                result = NamespaceDict(
                    stdout=stdout,
                    stderr=stderr,
                    returncode=process.returncode,
                    exit_status=process.returncode,
                )
    else:
        if background:
            if target_os == "windows":
                command = win_background_cmd
            else:
                command = f"{command} > /dev/null 2>&1 &"
        result = await con.run(command, **kwargs)
    return result


async def tunnel(hub, name: str, remote: str, local: str):
    """
    Given the local and remote addrs create a tcp tunnel through the connection
    """
    con = hub.tunnel.asyncssh.CONS[name]["con"]
    await con.forward_remote_port("", remote, "localhost", local)
    return True


async def destroy(hub, name: str):
    """
    Destroy the named connection
    """
    con = hub.tunnel.asyncssh.CONS[name]["con"]
    con.close()
    await con.wait_closed()
    return True


def connected(hub, name: str):
    """
    Determine whether the connection is
    connected or disconnected.
    """
    return hub.tunnel.asyncssh.CONS[name]["con"]._transport
