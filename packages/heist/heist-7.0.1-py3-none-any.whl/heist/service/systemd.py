async def disable(hub, tunnel_plugin, target_name, service):
    ret = await hub.tunnel[tunnel_plugin].cmd(
        target_name, f"systemctl disable {service}"
    )
    if ret.exit_status != 0:
        hub.log.error(ret.stderr)
        return False
    return True


async def enable(hub, tunnel_plugin, target_name, service):
    ret = await hub.tunnel[tunnel_plugin].cmd(
        target_name, f"systemctl enable {service}"
    )
    if ret.exit_status != 0:
        hub.log.error(ret.stderr)
        return False
    return True


async def start(hub, target_name, tunnel_plugin, service, block=True, **kwargs):
    cmd = [f"systemctl start {service}"]
    if not block:
        cmd.append("--no-block")
    ret = await hub.tunnel[tunnel_plugin].cmd(target_name, " ".join(cmd))
    if ret.exit_status != 0:
        hub.log.error(ret.stderr)
        return False
    return True


async def stop(hub, target_name, tunnel_plugin, service, target_os="linux"):
    ret = await hub.tunnel[tunnel_plugin].cmd(target_name, f"systemctl stop {service}")
    if ret.exit_status != 0:
        hub.log.error(ret.stderr)
        return False
    return True


async def restart(hub, target_name, tunnel_plugin, service):
    ret = await hub.tunnel[tunnel_plugin].cmd(
        target_name, f"systemctl restart {service}"
    )
    if ret.exit_status != 0:
        hub.log.error(ret.stderr)
        return False
    return True


def conf_path(hub, service_name):
    return hub.tool.path.path_convert(
        "linux", "/etc", ["systemd", "system", f"{service_name}.service"]
    )


async def clean(hub, target_name, tunnel_plugin, service):
    await hub.tunnel[tunnel_plugin].cmd(target_name, f"systemctl daemon-reload")


async def status(hub, target_name, tunnel_plugin, service, **kwargs):
    cmd = [f"systemctl status {service}"]
    ret = await hub.tunnel[tunnel_plugin].cmd(target_name, " ".join(cmd))
    if ret.exit_status != 0:
        hub.log.error(ret.stderr)
        return False
    return True
