import time


async def disable(hub, tunnel_plugin, target_name, service):
    pass


async def enable(hub, tunnel_plugin, target_name, service):
    pass


async def start(
    hub,
    target_name,
    tunnel_plugin,
    service,
    run_cmd=None,
    target_os="linux",
    run_dir=None,
    background=False,
    **kwargs,
):
    """
    Start the service in the background
    """
    # each heist manager will need to have a function
    # that validates the run_cmd input
    if not hub.tool.service.valid_run_cmd(run_cmd, run_dir, target_os=target_os):
        hub.log.error(
            f"The run command is not valid. Not starting the service {service}"
        )
        return False
    cmd = [f"{run_cmd}"]
    hub.log.info(f"Starting the service {service}")
    ret = await hub.tunnel[tunnel_plugin].cmd(
        target_name, " ".join(cmd), background=background, target_os=target_os
    )
    if ret.returncode != 0:
        hub.log.error(ret.stderr)
        return False
    return True


async def stop(hub, target_name, tunnel_plugin, service, target_os="linux"):
    """
    Stop the service
    """
    if target_os == "windows":
        kill_cmd = (
            f'powershell -command "Stop-Process -Name {service} -ErrorAction SilentlyContinue; '
            'If ($?) { exit 0 } else { exit 1 }"'
        )
    else:
        kill_cmd = f"pkill -f {service}"
    hub.log.debug(f"Attempting to kill {service} with: {kill_cmd}")
    ret = await hub.tunnel[tunnel_plugin].cmd(
        target_name, kill_cmd, target_os=target_os
    )
    if ret.exit_status != 0:
        hub.log.error(ret.stderr)
        return False
    hub.log.info(f"Successfully killed {service}")
    return True


async def restart(
    hub,
    target_name,
    tunnel_plugin,
    service,
    run_cmd=None,
    target_os="linux",
    run_dir=None,
    **kwargs,
):
    if await hub.service.raw.status(
        target_name, tunnel_plugin, service, target_os=target_os
    ):
        if not await hub.service.raw.stop(
            target_name, tunnel_plugin, service, target_os=target_os
        ):
            hub.log.error(f"Could not stop the service {service}")
            return False
        time.sleep(2)
    while not hub.service.raw.status(
        target_name, tunnel_plugin, service, target_os=target_os
    ):
        time.sleep(5)
        continue
    if not await hub.service.raw.start(
        target_name,
        tunnel_plugin,
        service,
        run_cmd=run_cmd,
        target_os=target_os,
        run_dir=run_dir,
    ):
        hub.log.error(f"Could not start the service {service}")
        return False
    return True


def conf_path(hub, service_name):
    pass


async def clean(hub, target_name, tunnel_plugin, service):
    pass


async def status(hub, target_name, tunnel_plugin, service, target_os="linux", **kwargs):
    cmd = [f"pgrep -f {service}"]
    if target_os == "windows":
        cmd = [f'powershell -command "get-process {service}"']
    ret = await hub.tunnel[tunnel_plugin].cmd(
        target_name, " ".join(cmd), target_os=target_os, sudo=kwargs.get("sudo")
    )
    if ret.returncode != 0:
        hub.log.info(f"The service {service} is not running")
        return False
    hub.log.info(f"The service {service} is running")
    return True
