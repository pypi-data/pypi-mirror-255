import os.path


def _get_defaults(os_name: str) -> dict[str, str]:
    if os_name == "nt":
        PROGRAM_DATA = os.environ.get("ProgramData", "C:\\ProgramData")

        defaults = {
            "config": f"{PROGRAM_DATA}\\heist\\heist.conf",
            "roster_dir": f"{PROGRAM_DATA}\\heist\\rosters",
            "roster_file": f"{PROGRAM_DATA}\\heist\\roster",
            "artifacts": f"{PROGRAM_DATA}\\heist\\artifacts",
        }

    try:
        is_root = os.getuid() == 0
    except:
        is_root = False

    if is_root:
        defaults = {
            "config": "/etc/heist/heist.conf",
            "roster_dir": "/etc/heist/rosters",
            "roster_file": "/etc/heist/roster",
            "artifacts": "/var/tmp/heist/artifacts",
        }
    else:
        home = os.path.expanduser("~/.heist")
        os.makedirs(home, exist_ok=True)
        defaults = {
            "config": f"{home}/config",
            "roster_dir": f"{home}/rosters",
            "roster_file": f"{home}/roster.yaml",
            "artifacts": f"{home}/artifacts",
        }

    # If the path doesn't exist then set the default to None
    if defaults.get("config"):
        if not os.path.exists(defaults["config"]):
            defaults["config"] = None

    return defaults


OS_DEFAULTS = _get_defaults(os.name)

CLI_CONFIG = {
    "config": {"options": ["-c"], "subcommands": ["_global_"], "os": "HEIST_CONFIG"},
    "artifacts_dir": {"subcommands": ["_global_"]},
    "roster": {"subcommands": ["_global_"]},
    "roster_dir": {"subcommands": ["_global_"]},
    "roster_file": {"options": ["-R"], "subcommands": ["_global_"]},
    "roster_data": {"subcommands": ["_global_"]},
    "checkin_time": {"subcommands": ["_global_"]},
    "dynamic_upgrade": {"subcommands": ["_global_"]},
    "renderer": {"subcommands": ["_global_"]},
    "target": {"options": ["--tgt", "-t"], "subcommands": ["_global_"]},
    "artifact_version": {"options": ["-a, --artifact"], "subcommands": ["_global_"]},
    "service_plugin": {"options": ["-s", "--service"], "subcommands": ["_global_"]},
    "manage_service": {"options": ["--service-status"], "subcommands": ["_global_"]},
    "auto_service": {"subcommands": ["_global_"]},
    "output": {
        "subcommands": ["_global_"],
        "source": "rend",
        "loaded_mod_choices_ref": "output",
    },
    "clean": {
        "options": ["--clean"],
        "action": "store_true",
        "subcommands": ["_global_"],
    },
    "noclean": {
        "options": ["--noclean"],
        "action": "store_true",
        "subcommands": ["_global_"],
    },
}
CONFIG = {
    "config": {
        "default": OS_DEFAULTS.get("config"),
        "help": "Heist configuration location",
    },
    "output": {"source": "rend", "default": "heist"},
    "artifacts_dir": {
        "default": OS_DEFAULTS.get("artifacts"),
        "help": "The location to look for artifacts that will be sent to target systems",
    },
    "roster": {
        "default": None,
        "help": "The type of roster to use to load up the remote systems to tunnel to",
    },
    "roster_dir": {
        "default": OS_DEFAULTS.get("roster_dir"),
        "help": "The directory to look for rosters",
    },
    "roster_file": {
        "options": ["-R"],
        "default": OS_DEFAULTS.get("roster_file"),
        "help": "Use a specific roster file, "
        "if this option is not used then the roster_dir will be used to find roster files",
    },
    "roster_data": {
        "default": None,
        "help": "Pass json data to be used for the roster data",
    },
    "checkin_time": {
        "default": 60,
        "type": int,
        "help": "The number of seconds between checking to see if the managed system needs to get an updated binary "
        "or agent restart.",
    },
    "dynamic_upgrade": {
        "default": False,
        "action": "store_true",
        "help": "Tell heist to detect when new binaries are available and dynamically upgrade target systems",
    },
    "renderer": {
        "default": "yaml",
        "help": "Specify the renderer to use to render heist roster files",
    },
    "target": {
        "options": ["--tgt", "-t"],
        "default": "",
        "help": "target used for multiple rosters",
    },
    "artifact_version": {
        "default": "",
        "help": "Version of the artifact to use for heist",
    },
    "roster_defaults": {
        "default": {},
        "type": dict,
        "help": "Default options to use for all rosters. CLI options will"
        "override these defaults",
    },
    "service_plugin": {
        "default": "raw",
        "help": "The type of service to use when managing the artifacts service status",
    },
    "auto_service": {
        "default": False,
        "type": bool,
        "help": "Auto detect the service manager to use on start up of service.",
    },
    "noclean": {
        "default": False,
        "action": "store_true",
        "help": "Whether to clean the deployed artifact and configurations",
    },
    "run_dir_root": {
        "default": False,
        "help": "Directory location on remote system for root deployment",
    },
}
SUBCOMMANDS = {
    # The manager determines how you want to create the tunnels and if you want to deploy
    # ephemeral agents to the remote systems
    "test": {x: "" for x in ("help", "desc")}
}
DYNE = {
    "artifact": ["artifact"],
    "heist": ["heist"],
    "roster": ["roster"],
    "service": ["service"],
    "tunnel": ["tunnel"],
    "output": ["output"],
    "tool": ["tool"],
}
