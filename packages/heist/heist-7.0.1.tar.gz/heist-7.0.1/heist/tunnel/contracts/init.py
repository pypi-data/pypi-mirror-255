async def sig_create(hub, name: str, target, **kwargs):
    pass


async def sig_send(hub, name: str, source: str, dest: str, **kwargs):
    pass


async def sig_get(hub, name: str, source: str, dest: str):
    pass


async def sig_cmd(hub, name: str, command: str, **kwargs):
    pass


async def sig_tunnel(hub, name: str, remote: str, local: str):
    pass


async def sig_destroy(hub, name: str):
    pass
