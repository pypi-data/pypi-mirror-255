import hashlib
import os
import pathlib
import re
import shutil
import tempfile
import warnings

import aiohttp.client_exceptions


def __init__(hub):
    hub.artifact.ACCT = ["artifact"]


async def extract(
    hub,
    target_name,
    tunnel_plugin,
    tmpdir=None,
    binary=None,
    run_dir=None,
    target_os="linux",
):
    """
    Extract the binary on the target.
    Uses tar for linux and unzip for windows.

    .. versionchanged:: v6.3.0
    """
    path = run_dir / pathlib.Path(binary).name

    if not hub.tool.path.clean_path(run_dir, pathlib.Path(binary).name):
        hub.log.error(f"The run_dir directory {run_dir} is not a valid path.")
        return False

    if tmpdir:
        warnings.warn(
            "The kwarg tmpdir is no longer used and will be removed in version v6.4.0"
        )
    if target_os == "linux":
        cmd = f"tar -xvf {path} --directory={run_dir}"
    elif target_os == "windows":
        cmd = f'powershell -command "$ProgressPreference = "SilentlyContinue"; Expand-Archive -LiteralPath "{path}" -DestinationPath {run_dir}"'
    ret = await hub.tunnel[tunnel_plugin].cmd(target_name, cmd, target_os=target_os)
    if ret.returncode == 0:
        return True
    hub.log.error(f"Could not extract {path} on the target")
    return False


def verify(hub, location, hash_value, hash_type="sha256"):
    with open(location, "rb") as fp:
        file_hash = getattr(hashlib, hash_type)(fp.read()).hexdigest()
        if not file_hash == hash_value:
            return False
    return True


async def fetch(hub, session, url, download=False, location=False):
    """
    Fetch a url and return json. If downloading artifact
    return the download location.
    """
    async with session.request("GET", url) as resp:
        if resp.status == 200:
            if download:
                with open(location, "wb") as fn_:
                    fn_.write(await resp.read())
                return location
            try:
                return await resp.json()
            except aiohttp.client_exceptions.ContentTypeError:
                return await resp.text()
        hub.log.critical(f"Cannot query url {url}. Returncode {resp.status} returned")
        return False


async def get(
    hub,
    artifact_name: str,
    target_os: str,
    version: str = None,
    repo_data=None,
    artifacts_dir=None,
    **kwargs,
):
    """
    Fetch a url return the download location.
    """
    if artifacts_dir is None:
        artifacts_dir = pathlib.Path(hub.OPT.heist.artifacts_dir)

    async with aiohttp.ClientSession() as session:
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Download and verify the designated Heist manager artifact
            tmp_artifact_location = await hub.artifact[artifact_name].get(
                target_os=target_os,
                version=version,
                repo_data=repo_data,
                session=session,
                tmpdirname=pathlib.Path(tmpdirname),
                **kwargs,
            )
            if not tmp_artifact_location:
                return False

            artifact_location = artifacts_dir / tmp_artifact_location.name
            if not hub.tool.path.clean_path(artifacts_dir, tmp_artifact_location.name):
                hub.log.error(
                    f"The tmp artifact {tmp_artifact_location.name} is not in the correct directory"
                )
                return False

            # artifact is already downloaded we do not need to copy/check
            if tmp_artifact_location == artifact_location:
                return True

            hub.log.info(
                f"Copying the artifact {artifact_location.name} to {str(artifacts_dir)}"
            )
            shutil.move(tmp_artifact_location, artifact_location)

    # ensure artifact was downloaded
    if not any(str(version) in x for x in os.listdir(str(artifacts_dir))):
        hub.log.critical(
            f"Did not find the {version} artifact in {str(artifacts_dir)}."
            f" Untarring the artifact failed or did not include version"
        )
        return False
    return artifact_location


def version(hub):
    # TODO Determine which artifact to use, find the right plugin, and find out the target's version of the artifact
    ...


async def deploy(
    hub,
    target_name,
    tunnel_plugin,
    run_dir,
    binary,
    artifact_name,
    target_os="linux",
    run_dir_root=None,
    **kwargs,
):
    """
    Deploy the artifact
    """
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")
    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        hub.log.error(f"The run_dir path {run_dir} is not valid")
        return False

    cmd = "\n".join(
        [
            s.strip()
            for s in f"""/bin/sh << 'EOF'
if [ -d {run_dir.parent} ]; then
    ls {run_dir.parent};
    exit 0
else
    echo "The {run_dir.parent} does not exist. Deploying artifact"
    exit 1
fi
EOF""".split(
                "\n"
            )
        ]
    )

    if target_os == "windows":
        cmd = (
            "powershell -command "
            + '"'
            + "; ".join(
                [
                    f"$Folder = '{run_dir.parent}'",
                    "if (Test-Path -Path $Folder) {Get-ChildItem -name $Folder} else {exit 1}",
                ]
            )
            + '"'
        )

    # check if there was a previous heist deployment
    use_prev = False
    prev_artifact = None
    prev = await hub.tunnel[tunnel_plugin].cmd(target_name, cmd, target_os=target_os)
    if prev.returncode == 1:
        ret = await hub.artifact[artifact_name].deploy(
            target_name,
            tunnel_plugin,
            run_dir,
            binary,
            target_os=target_os,
            run_dir_root=run_dir_root,
            **kwargs,
        )
    else:
        run_dir = run_dir.parent / prev.stdout.strip()
        get_binary = f"ls {run_dir}/"
        use_prev = True
        ret = await hub.artifact[artifact_name].deploy(
            target_name,
            tunnel_plugin,
            run_dir,
            binary,
            run_dir_root=run_dir_root,
            target_os=target_os,
            # TODO no.  When verify=True this should be a separate function, not overloading the deploy function
            verify=True,
            **kwargs,
        )
        artifact_files = await hub.tunnel[tunnel_plugin].cmd(
            target_name, get_binary, target_os=target_os
        )
        suffix = hub.tool.artifacts.get_artifact_suffix(target_os=target_os)
        prev_artifact = [x for x in artifact_files.stdout.split() if suffix in x]
        if prev_artifact:
            prev_artifact = prev_artifact[0]
    return run_dir, ret, use_prev, prev_artifact


async def verify_checksum(
    hub,
    target_name,
    tunnel_plugin,
    run_dir,
    source_fp,
    target_fp,
    target_os="linux",
    hash_type=None,
):
    """
    Verify checksum file
    """
    pathlib.Path(source_fp.parent).mkdir(parents=True, exist_ok=True)
    if hash_type is None:
        hash_type = "sha512"

    # validating hash_type
    if not getattr(hashlib, hash_type):
        hub.log.error(f"hash_type of {hash_type} is not valid")
        return False

    # validate paths
    if not hub.tool.path.clean_path(run_dir, target_fp):
        hub.log.error(f"Path is not valid: {target_fp}")
        return False
    if not pathlib.Path(source_fp).is_file():
        hub.log.error(f"Source path does not exist: {source_fp}")
        return False
    if not hub.tool.path.clean_path(
        hub.tool.artifacts.get_artifact_dir(target_os=target_os), source_fp
    ):
        hub.log.error(f"Source path is not valid: {source_fp}")
        return False

    if target_os == "windows":
        cmd = (
            "powershell -command "
            + '"'
            + "; ".join(
                [
                    f"Get-ChildItem -Recurse {target_fp.parent} | Get-FileHash -Algorithm {hash_type.upper()} | Format-List"
                ]
            )
            + '"'
        )
    else:
        cmd = f"cd {run_dir}; {hash_type}sum -c {target_fp}"
    ret = await hub.tunnel[tunnel_plugin].cmd(target_name, cmd, target_os=target_os)
    if ret.returncode != 0:
        hub.log.error(f"Could not verify the checksum of the artifact")
        return False
    if target_os == "windows":
        target_data = {}
        for line in ret.stdout.split(" : "):
            line = line.strip()
            if line.startswith(("Algorithm", "SHA")):
                continue
            if "\nPath" in line:
                _hash = "".join(line.split()).replace("Path", "")
                continue
            if "\nAlgorithm" in line:
                _path = line.split()[0]
            target_data[_hash] = _path
    else:
        cmd = f"cat {target_fp}"
        ret = await hub.tunnel[tunnel_plugin].cmd(target_name, cmd, target_os=target_os)

    with open(source_fp) as fp:
        data = fp.read()
        if target_os == "windows":
            items = iter(data.split())
            source_data = dict(zip(items, items))
            test = {}
            for key, value in source_data.items():
                key = key.upper()
                getattr(hashlib, hash_type)().block_size
                check = r"([a-fA-F\d]){128}"
                is_hash = re.match(check, key)
                if is_hash:
                    _hash = key
                    _path = value
                else:
                    is_hash = re.match(check, value)
                    if is_hash:
                        _hash = value.upper()
                        _path = key

                test[_hash] = _path

                if not target_data.get(_hash):
                    hub.log.error(
                        f"Could not verify the checksum of the artifact for {_hash} and {_path}"
                    )
                    return False
                else:
                    target_data[_hash] == _path

        else:
            if data != ret.stdout:
                hub.log.error(f"Could not verify the checksum of the artifact")
                return False
    return ret


def checksum(hub, files, hash_type=None):
    """
    Create checksum for files to be copied over
    for the artifact.
    """
    if not hash_type:
        hash_type = "sha512"

    # validating hash_type
    if not getattr(hashlib, hash_type):
        hub.log.error(f"hash_type of {hash_type} is not valid")
        return False

    ret = {}
    for fp in files:
        fp = pathlib.Path(fp)
        if not fp.exists():
            hub.log.error(f"Could not create checksum. Path {fp} does not exist")
            return False
        hash_obj = getattr(hashlib, hash_type)()
        count = 1
        if fp.is_file():
            hash_obj.update(open(fp, "rb").read())
            ret[hash_obj.hexdigest()] = fp
        if fp.is_dir():
            for _fp in fp.rglob("*"):
                hash_obj = getattr(hashlib, hash_type)()
                count += 1
                if _fp.is_file():
                    hash_obj.update(open(_fp, "rb").read())
                    ret[hash_obj.hexdigest()] = _fp
    return ret


async def clean(hub, target_name, tunnel_plugin):
    """
    Clean up the deployed artifact and files
    """
    # remove run directory
    run_dir = hub.heist.CONS[target_name]["run_dir"]
    target_os, _ = await hub.tool.system.os_arch(target_name, tunnel_plugin)

    # clean alias symlinks
    if target_os == "linux":
        scripts_dir = run_dir / "scripts"
        cmd_alias = f"ls {scripts_dir}"
        get_files = await hub.tunnel[tunnel_plugin].cmd(
            target_name, cmd_alias, target_os=target_os
        )
        if get_files.returncode != 0:
            hub.log.error("Did not find alias files. Not removing")
        else:
            for _file in get_files.stdout.split():
                _file = str(scripts_dir / _file)
                find_symlink = f"find -L /usr/bin/ -samefile {_file}"
                get_symlink = await hub.tunnel[tunnel_plugin].cmd(
                    target_name, find_symlink, target_os=target_os
                )
                if get_symlink.returncode != 0:
                    hub.log.error(f"Could not find the symlink to script {_file}")
                    break
                rm_symlink = f"rm {get_symlink.stdout.strip()}"
                rm_symlink = await hub.tunnel[tunnel_plugin].cmd(
                    target_name, rm_symlink, target_os=target_os
                )
                if rm_symlink.returncode != 0:
                    hub.log.error(f"Could not remove the symlink of file {_file}")
                    break

    if target_os == "windows":
        cmd_isdir = f'powershell -command "If ( (Get-Item {run_dir}).PSIsContainer ) {{ exit 0 }} Else {{ exit 1 }}"'
        cmd_rmdir = f'powershell -command "cmd /c rmdir /s /q {run_dir}"'
    else:
        cmd_isdir = f"[ -d {run_dir} ]"
        cmd_rmdir = f"rm -rf {run_dir}"

    # Make sure it is a directory
    ret = await hub.tunnel[tunnel_plugin].cmd(
        target_name, cmd_isdir, target_os=target_os
    )
    if ret.returncode == 0:
        await hub.tunnel[tunnel_plugin].cmd(target_name, cmd_rmdir, target_os=target_os)

    # remove parent directory if its empty
    # If it's not empty, there might be another running instance of heist that
    # was previously deployed
    await hub.tunnel[tunnel_plugin].cmd(
        target_name,
        f"rmdir {hub.heist.CONS[target_name]['run_dir'].parent}",
        target_os=target_os,
    )


async def create_aliases(hub, content, aliases=None, target_os="linux"):
    """
    Create the alias files that will be sent
    to the target
    """
    artifacts_dir = (
        pathlib.Path(hub.tool.artifacts.get_artifact_dir(target_os=target_os))
        / "scripts"
    )
    artifacts_dir.mkdir(exist_ok=True)
    # aliases should follow the dictionary structure:
    # {"binary-name": {"file": "path_to_binary_to_copy", "cmd": "cmd used to run on target"},
    #  "binary-name2": {"file": "path_to_binary_to_copy", "cmd": "cmd used to run on target"}}
    for alias in aliases:
        alias_file = aliases[alias]["file"]
        alias_cmd = aliases[alias]["cmd"]
        if target_os == "windows":
            alias_file = alias_file.parent / f"{alias_file.name}.bat"
        # this requires {alias} to be in the content.
        alias_content = content.format(alias=alias_cmd)
        with open(alias_file, "w") as fp:
            fp.write(alias_content)
        alias_file.chmod(0o711)
    return True


async def deploy_aliases(
    hub, target_name, tunnel_plugin, run_dir, aliases_dir, target_os="linux"
):
    """
    Deploy the aliases files to the target
    and setup correct path environment variables
    """
    artifacts_dir = (
        pathlib.Path(hub.tool.artifacts.get_artifact_dir(target_os=target_os))
        / "scripts"
    )
    await hub.tunnel[tunnel_plugin].send(
        target_name,
        artifacts_dir,
        run_dir,
        preserve=True,
        recurse=True,
    )
    if target_os == "windows":
        path_cmd = f'powershell -command "setx PATH "{aliases_dir};$env:PATH""'
        ret = await hub.tunnel[tunnel_plugin].cmd(
            target_name, path_cmd, target_os=target_os
        )
        if ret.returncode != 0:
            hub.log.error(f"Could not add {artifacts_dir} to windows PATH environment")
            return False
    else:
        path_cmd = f"ln -s {aliases_dir}/* /usr/bin/"
        ret = await hub.tunnel[tunnel_plugin].cmd(
            target_name, path_cmd, target_os=target_os
        )
        if ret.returncode != 0:
            hub.log.error(f"Could not add aliases to PATH")
            return False
    return True
