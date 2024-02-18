async def os_arch(hub, target_name: str, tunnel_plugin: str) -> tuple[str, str]:
    """
    Query the system for the OS and architecture type
    """
    DELIM = "'|'"
    ret = await hub.tunnel[tunnel_plugin].cmd(
        target_name,
        f'echo "$OSTYPE{DELIM}$MACHTYPE{DELIM}$env:PROCESSOR_ARCHITECTURE"'
        # target_name, f'echo "$OSTYPE|$MACHTYPE|$env:PROCESSOR_ARCHITECTURE"'
    )
    assert not ret.returncode, ret.stderr
    kernel, arch, winarch = ret.stdout.lower().split("|", maxsplit=2)

    # Set the architecture bit
    if "64" in winarch or "64" in arch:
        os_arch = "amd64"
    else:
        os_arch = "i386"

    # Set the kernel bit
    if "linux" in kernel:
        kernel = "linux"
    elif "darwin" in kernel:
        kernel = "darwin"
    elif "bsd" in kernel:
        kernel = "bsd"
    elif "PROCESSOR_ARCHITECTURE" not in winarch:
        kernel = "windows"
    else:
        raise ValueError(
            f"Could not determine arch from kernel: {kernel} arch: {arch} winarch: {winarch}"
        )
    hub.log.debug(f'Detected kernel "{kernel}" on target')
    hub.log.debug(f'Detected arch "{os_arch}" on target')
    return kernel, os_arch
