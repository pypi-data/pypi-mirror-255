DEFAULT_TUNNEL = "asyncssh"


async def sig_run(
    hub,
    remotes: dict[str, dict[str, str]],
    *,
    artifact_version,
    manage_service,
    roster_file: str,
    roster: str,
    **kwargs
):
    ...


def _validate_remote(remote: dict[str, str]):
    if not remote.get("tunnel"):
        remote["tunnel"] = DEFAULT_TUNNEL
    return remote


async def call_run(hub, ctx):
    kwargs = ctx.get_arguments()
    remotes = kwargs.pop("remotes")

    validate_remotes = {}
    for id_, remote in remotes.items():
        validate_remotes[id_] = _validate_remote(remote)

    kwargs.update(**kwargs.pop("kwargs", {}))
    manage_service = kwargs.pop("manage_service", None)
    artifact_version = kwargs.pop("artifact_version", None)
    return await ctx.func(
        kwargs.pop("hub"),
        remotes=validate_remotes,
        artifact_version=artifact_version,
        manage_service=manage_service,
        **kwargs
    )
