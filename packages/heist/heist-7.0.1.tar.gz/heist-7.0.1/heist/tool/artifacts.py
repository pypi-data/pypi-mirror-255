import pathlib


def get_artifact_dir(hub, target_os="linux"):
    """
    function to get the full path to artifacts directory
    with the pkg_type included
    """
    artifacts_dir = pathlib.Path(hub.OPT.heist.artifacts_dir, "onedir", target_os)
    if not artifacts_dir.is_dir():
        artifacts_dir.mkdir(parents=True)
    return str(artifacts_dir)


def get_artifact_suffix(hub, target_os="linux"):
    """
    return the suffix for an artifact for
    each targeted OS.
    """
    suffix = "tar.xz"
    if target_os == "windows":
        suffix = ".zip"
    return suffix
