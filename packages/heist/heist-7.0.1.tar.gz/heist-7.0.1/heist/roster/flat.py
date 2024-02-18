import os
import pathlib
from typing import Any


async def read(hub, roster_file: str = "") -> dict[str, Any]:
    """
    Read in the data from the configured rosters
    """
    ret = {}
    rend = hub.OPT.heist.renderer

    if pathlib.Path(roster_file).is_file():
        return await hub.rend.init.parse(roster_file, rend)
    else:
        hub.log.error(f"Missing roster file: {roster_file}")

    if pathlib.Path(hub.OPT.heist.roster_dir).is_dir():
        for fn in os.listdir(hub.OPT.heist.roster_dir):
            full = os.path.join(hub.OPT.heist.roster_dir, fn)
            ret.update(await hub.rend.init.parse(full, rend))
    return ret
