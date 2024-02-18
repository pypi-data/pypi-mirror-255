async def run(hub, remotes: dict[str, dict[str, str]], artifact_version=None, **kwargs):
    ret = [{"result": "Success", "comment": "No problems encountered", "retvalue": 0}]
    hub.log.info(
        "This is a test heist manager. You have installed heist correctly. "
        "Install a heist manager to use full functionality"
    )
    return ret
