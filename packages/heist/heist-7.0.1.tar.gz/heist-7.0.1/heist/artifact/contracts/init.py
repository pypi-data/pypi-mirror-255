import pkg_resources


def pre_get(hub, ctx):
    kwargs = ctx.get_arguments()
    version = kwargs.get("version")
    kwargs.get("repo_data")
    if version:
        check_ver = version
        if "-" in version:
            check_ver, pkg_ver = version.split("-")
            assert isinstance(int(pkg_ver), int)
        valid_version = pkg_resources.safe_version(check_ver)
        assert check_ver == valid_version, f"version {check_ver} is not valid"
