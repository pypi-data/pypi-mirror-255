import json
from typing import Any

import rend.exc


def generate_roster_data(hub, roster_data, roster_file=None):
    """
    Using json parse the data pass in by roster_data.
    If roster_file is also passed, write the roster_data
    to the given file.
    """
    try:
        ret = hub.rend.json.render(roster_data)
    except rend.exc.RenderException:
        hub.log.error("Invalid json data in roster_data")
        return False

    if roster_file:
        with open(roster_file, "w+") as fp_:
            json.dump(ret, fp_)
    return ret


async def read(
    hub, roster: str = None, roster_file: str = "", roster_data=None
) -> dict[str, Any]:
    """
    Given the rosters to read in, the tgt and the tunnel_plugin
    """
    ret = {}

    ready = False
    if roster_data:
        ready = hub.roster.init.generate_roster_data(
            roster_data, roster_file=roster_file
        )

    # If a specific roster plugin wasn't specified then determine the best roster plugin automatically
    if roster is None:
        if roster_file.endswith(".fernet"):
            roster = "fernet"
        else:
            roster = "flat"
        hub.log.info(f"Picking default roster: {roster}")

    if not ready:
        ready = await hub.roster[roster].read(roster_file)

    if not ready:
        raise ValueError(f"The roster {roster} did not return data when rendered")

    if not isinstance(ready, dict):
        raise ValueError(f"The roster {roster} is not formatted correctly")

    for id_, condition in ready.items():
        if not isinstance(condition, dict):
            raise ValueError(f"The roster {roster} is not formatted correctly.")
        ret[condition.get("id", id_)] = condition
        if "id" not in condition:
            condition["id"] = id_

        ret[condition["id"]] = condition

    return ret
