from collections.abc import Mapping
from typing import Any


def sig_read(hub, roster_file: str = "") -> dict[str, Any]:
    ...


async def post_read(hub, ctx):
    ret = ctx.ret or {}
    for data in ret.values():
        assert isinstance(data, Mapping)
    return ret
