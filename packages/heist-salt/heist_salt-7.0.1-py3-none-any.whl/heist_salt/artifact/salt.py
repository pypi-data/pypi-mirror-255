"""
    artifact module to manage the download of salt artifacts
"""
import json
import os
import pathlib
import re
import tarfile
import tempfile
import urllib
import zipfile
from pathlib import Path

import aiohttp
from packaging.version import Version


async def repo_data(hub, salt_repo_url):
    """
    Query repo.json file to gather the repo data
    """
    salt_repo_url = urllib.parse.urljoin(salt_repo_url, "repo.json")
    async with aiohttp.ClientSession() as session:
        data = await hub.artifact.init.fetch(session, salt_repo_url)
        if isinstance(data, str):
            data = json.loads(data)
        if not data:
            hub.log.critical(
                f"Query to {salt_repo_url} failed, falling back to"
                f"pre-downloaded artifacts"
            )
            return False
        return data


async def get(
    hub,
    target_os: str = "linux",
    version: str = "",
    repo_data: dict = None,
    salt_repo_url: str = "",
    session=None,
    tmpdirname=None,
) -> str:
    """
    Download artifact if does not already exist.
    """
    # TODO: add in arch detection support for the target
    arch = "x86"
    major = version.split(".")[0]
    suffix = hub.tool.artifacts.get_artifact_suffix(target_os=target_os)
    try:
        artifact = [
            x
            for x in repo_data[major].keys()
            if target_os in x and arch in x and version in x and suffix in x
        ][0]
    except IndexError:
        hub.log.error(f"The version {version} was not found for {target_os}")
        return False
    repo_data = repo_data[major][artifact]
    verify_artifact = re.compile(f"salt-{version}.*{target_os}.*")
    if not verify_artifact.search(artifact):
        hub.log.error(f"The artifact {artifact} is not a valid Salt artifact")
        return False
    artifact_url = urllib.parse.urljoin(salt_repo_url, major + "/" + artifact)
    if not isinstance(tmpdirname, Path):
        hub.log.error(f"The tmp dir {tmpdirname} is not a pathlib.Path instance")
        return False

    if not isinstance(session, aiohttp.ClientSession):
        hub.log.error(f"The session is not a aiohttp.ClientSession instance")
        return False

    # Ensure that artifact directory exists
    artifacts_dir = hub.tool.artifacts.get_artifact_dir(target_os=target_os)
    location = Path(artifacts_dir, artifact)
    if not hub.tool.path.clean_path(artifacts_dir, artifact):
        hub.log.error(f"The {artifact} is not in the correct directory")
        return False

    # check to see if artifact already exists
    suffix = pathlib.Path
    if hub.artifact.salt.latest(
        "salt",
        version=version,
        suffix=pathlib.Path(artifact).suffix,
        target_os=target_os,
    ):
        hub.log.info(f"The Salt artifact {version} already exists")
        return location

    # download artifact
    hub.log.info(f"Downloading the artifact {artifact} to {artifacts_dir}")
    tmp_artifact_location = Path(tmpdirname) / artifact
    await hub.artifact.init.fetch(
        session, artifact_url, download=True, location=tmp_artifact_location
    )
    if not hub.artifact.init.verify(
        tmp_artifact_location,
        hash_value=repo_data["SHA3_512"],
        hash_type="sha3_512",
    ):
        hub.log.critical(f"Could not verify the hash of {location}")
        return False
    hub.log.info(f"Verified the hash of the {artifact} artifact")
    return tmp_artifact_location


def latest(
    hub, name: str, version: str = "", suffix: str = "", target_os: str = "linux"
) -> str:
    """
    Given the artifacts directory return the latest desired artifact

    :param str version: Return the artifact for a specific version.
    """
    names = []
    paths = {}

    artifacts_dir = hub.tool.artifacts.get_artifact_dir(target_os=target_os)
    if not os.path.isdir(artifacts_dir):
        return ""
    for fn in os.listdir(artifacts_dir):
        if fn.startswith(name) and fn.endswith(suffix):
            ver = fn.split("-")[1]
            names.append(ver)
            paths[ver] = fn
    names = sorted(names, key=Version)
    if version:
        if version in names:
            return os.path.join(artifacts_dir, paths[version])
        else:
            return ""
    elif not paths:
        return ""
    else:
        return os.path.join(artifacts_dir, paths[names[-1]])


async def aliases(
    hub,
    target_name: str,
    tunnel_plugin: str,
    run_dir=None,
    run_dir_root=None,
    target_os="linux",
):
    """
    Set the aliases for the salt cmds
    """
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")
    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        hub.log.error(
            f"The path {run_dir} is not a valid path when attempting to deploy"
        )
        return False

    aliases, artifacts_dir, content = hub.heist[hub.SUBPARSER].generate_aliases(
        run_dir, run_dir_root=run_dir_root, target_os=target_os
    )
    aliases_dir = run_dir / "scripts" / artifacts_dir.name
    if not await hub.artifact.init.create_aliases(
        content, aliases=aliases, target_os=target_os
    ):
        hub.log.error(
            f"Could not create the alias files in the directory {artifacts_dir}"
        )
        return False
    if not await hub.artifact.init.deploy_aliases(
        target_name,
        tunnel_plugin,
        run_dir,
        aliases_dir=aliases_dir,
        target_os=target_os,
    ):
        hub.log.error(
            f"Could not deploy the alias files from the path {artifacts_dir} to the target"
        )
        return False
    return artifacts_dir


async def deploy(
    hub,
    target_name: str,
    tunnel_plugin: str,
    run_dir: str,
    binary: str,
    user=None,
    target_os="linux",
    target_id=None,
    bootstrap=False,
    run_dir_root=None,
    verify=False,
    update=False,
):
    """
    Deploy the salt artifact to the remote system
    """
    root_dir = run_dir / "root_dir"
    binary_path = run_dir / "salt"
    is_windows = target_os == "windows"
    artifacts_dir = hub.tool.artifacts.get_artifact_dir(target_os=target_os)
    checksum_file = pathlib.Path(artifacts_dir, target_id, "code_checksum")
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")

    if not verify:
        is_windows = False
        if target_os == "windows":
            is_windows = True

        if not hub.tool.path.clean_path(run_dir_root, run_dir):
            hub.log.error(
                f"The path {run_dir} is not a valid path when attempting to deploy"
            )
            return False

        if not hub.tool.path.clean_path(
            hub.tool.artifacts.get_artifact_dir(target_os=target_os), binary
        ):
            hub.log.error(f"The binary path {binary} is not a valid path")
            return False

        conf_dir = pathlib.Path(artifacts_dir, target_id, "root_dir", "conf")
        conf_file, salt_opts = hub.heist[hub.SUBPARSER].get_salt_opts(
            run_dir,
            target_name,
            run_dir_root=run_dir_root,
            target_os=target_os,
            target_id=target_id,
            bootstrap=bootstrap,
        )
        conf_file = conf_dir / conf_file
        if not update:
            config = hub.tool.config.mk_config(
                target_name=target_name,
                config=salt_opts,
                conf_file=conf_file,
            )
            if not config:
                hub.log.error(
                    "Could not create the Salt configuration to copy to the target."
                )
                return False

            # create dirs and config
            hub.log.debug(
                f"Create and secure config dir and parent directories: {conf_dir}"
            )

            if is_windows:
                # Owner (OW), System (SY), and Administrators (BA) have Full Control
                sddl = "'D:PAI(A;OICI;FA;;;OW)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)'"
                owner = r"[System.Security.Principal.NTAccount]'BUILTIN\Administrators'"
                cmd = "; ".join(
                    [
                        f'powershell -command "New-Item -Path "{root_dir}" -Type Directory',
                        f'$acl = Get-Acl "{root_dir}"',
                        f'$acl.SetSecurityDescriptorSddlForm("{sddl}")',
                        f"$acl.SetOwner({owner})",
                        f'Set-Acl -Path "{root_dir}" -AclObject $acl"',
                    ]
                )
            else:
                perms = (
                    0o710
                    if hub.tunnel.asyncssh.CONS[target_name].get("sudo")
                    else 0o700
                )
                # mkdir will not add the correct permissions to the parent directories
                # unless each directory is specified
                cmd = f"mkdir -m{perms:o} -p {root_dir.parent.parent} {root_dir.parent} {root_dir}"
            ret = await hub.tunnel[tunnel_plugin].cmd(
                target_name, cmd, target_os=target_os
            )

            if user and not is_windows:
                ret = await hub.tunnel[tunnel_plugin].cmd(
                    target_name,
                    f"chown -R {user}:{user} {root_dir.parent.parent}",
                )

            if ret.returncode != 0 or ret.stderr:
                hub.log.error(f"Could not make {conf_dir} or {root_dir} on remote host")
                hub.log.error(ret.stderr)
                return False

        # Create tmp dir and unzip/untar the artifact and copy over
        hub.log.info(f"Preparing to ship salt to {root_dir}")
        copy_items = [binary, str(conf_dir.parent)]

        files = []
        if not update:
            if target_os != "windows":
                alias = await hub.artifact.salt.aliases(
                    target_name,
                    tunnel_plugin,
                    run_dir,
                    run_dir_root=run_dir_root,
                    target_os=target_os,
                )
                # We do not need to fail if the alias files do not get created.
                # Heist-Salt will still work, the user cannot use the salt aliases.
                if not alias:
                    hub.log.error(
                        "Creating and deploying the aliases failed. Will continue deploying"
                    )
                else:
                    files.append(str(alias))

        # generate checksum data to the checksum_file for the binary
        hub.artifact.salt.generate_checksum(
            binary, checksum_file, target_id, files=files, target_os=target_os
        )

        copy_items.append(str(checksum_file))

        # Copy the artifact to the run_dir
        await hub.tunnel[tunnel_plugin].send(
            target_name,
            copy_items,
            run_dir,
            preserve=True,
            recurse=True,
        )
        if not await hub.artifact.salt.extract_binary(
            target_name=target_name,
            tunnel_plugin=tunnel_plugin,
            binary=binary,
            binary_path=binary_path,
            run_dir=run_dir,
            target_os=target_os,
        ):
            return False

    # verify checksum
    if verify:
        # TODO why is this verify_checksum function being called when verify=True instead of just being called directly?
        ret = await hub.artifact.init.verify_checksum(
            target_name=target_name,
            tunnel_plugin=tunnel_plugin,
            run_dir=run_dir,
            source_fp=checksum_file,
            target_fp=root_dir.parent / checksum_file.name,
            target_os=target_os,
        )
        if not ret:
            # TODO this check always fails
            hub.log.error("Could not verify checksum")
            return False

    return binary_path


async def update(
    hub,
    target_name,
    tunnel_plugin,
    service_plugin,
    run_dir,
    target_id,
    run_dir_root=None,
    old_binary=None,
    new_binary=None,
    binary_path=None,
    target_os="linux",
):
    """
    Update the binary to the latest artifact and update the checksum file
    with new artifact data.
    """
    # validate all of the paths input
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")
    for path in [run_dir, binary_path]:
        if not hub.tool.path.clean_path(run_dir_root, path):
            hub.log.error(
                f"The path {run_dir} is not a valid path when attempting to update"
            )
            return False

    artifacts_dir = hub.tool.artifacts.get_artifact_dir(target_os=target_os)
    for path in [old_binary, new_binary]:
        if not hub.tool.path.clean_path(artifacts_dir, path):
            hub.log.error(
                f"The binary path {binary_path} is not a valid path when attempting to update"
            )
            return False

    hub.log.info(
        f"Updating the old binary {old_binary} to the latest binary {new_binary} for target {target_id}"
    )
    binary_path = run_dir / "salt"
    service_name = hub.heist[hub.SUBPARSER].get_service_name(
        service_plugin, target_os=target_os, start=False
    )

    if await hub.service.init.status(
        target_name, tunnel_plugin, service=service_name, target_os=target_os
    ):
        ret = await hub.service.init.stop(
            target_name, tunnel_plugin, service=service_name, target_os=target_os
        )
        if not ret:
            hub.log.error(
                f"Could not stop the service {service_name} for target {target_id}"
            )
            return False

    # clean old salt directory
    target_old_binary = run_dir / pathlib.Path(old_binary).name
    cmd_rmdir = f"rm -rf {binary_path}"
    cmd_rm_bin = f"rm {target_old_binary}"
    if target_os == "windows":
        cmd_rmdir = f"cmd /c rmdir /s /q {binary_path}"
        cmd_rm_bin = f"cmd /c del /s /q {target_old_binary}"
    hub.log.info(f"Cleaning old files in {binary_path} and {target_old_binary}")
    clean_dir = await hub.tunnel[tunnel_plugin].cmd(
        target_name, cmd_rmdir, target_os=target_os
    )

    if clean_dir.returncode != 0:
        hub.log.error(f"Could not delete the path {binary_path} on target {target_id}")
        hub.log.error(f"Could not update the previous binary {target_old_binary}")
        return False

    # clean old binary
    clean_binary = await hub.tunnel[tunnel_plugin].cmd(
        target_name, cmd_rm_bin, target_os=target_os
    )
    if clean_binary.returncode != 0:
        hub.log.error(
            f"Could not delete the path {target_old_binary} on target {target_id}"
        )
        hub.log.error(f"Could not update the previous binary {target_old_binary}")
        return False

    hub.log.info(f"Deploying the new artifact {new_binary} to target {target_id}")
    if not await hub.artifact.salt.deploy(
        target_name=target_name,
        tunnel_plugin=tunnel_plugin,
        run_dir=run_dir,
        binary=new_binary,
        target_os=target_os,
        target_id=target_id,
        update=True,
    ):
        hub.log.error(
            f"Could not deploy the new artifact {new_binary} to target {target_id}"
        )
        return False

    kwargs = {"target_id": target_id}
    run_cmd = hub.heist[hub.SUBPARSER].raw_run_cmd(
        service_plugin, run_dir, target_os=target_os, **kwargs
    )
    hub.log.info(f"Restarting the service {service_name} for target {target_id}")
    if not await hub.service.init.restart(
        target_name,
        tunnel_plugin,
        service=service_name,
        run_cmd=run_cmd,
        target_os=target_os,
        run_dir=run_dir,
    ):
        hub.log.error(
            f"Could not restart the service {service_name} for target {target_id}"
        )
        return False
    return True


def generate_checksum(
    hub, binary, checksum_file, target_id, files=None, target_os="linux"
):
    """
    function to generate the checksum file
    with the hashs of the binary
    """
    artifacts_dir = hub.tool.artifacts.get_artifact_dir(target_os=target_os)
    conf_dir = pathlib.Path(artifacts_dir, target_id, "root_dir", "conf")

    if files:
        for _file in files:
            if not isinstance(_file, pathlib.Path):
                _file = pathlib.Path(_file)
            for _fp in _file.rglob("*"):
                if not _fp.is_file():
                    hub.log.error(
                        f"The path {_file} does not exist. Cannot generate checksum"
                    )
                    return False

    for path in [binary, checksum_file, conf_dir]:
        if not hub.tool.path.clean_path(artifacts_dir, checksum_file):
            hub.log.error(f"The path {path} is not in the correct directory")
            return False

    for path in [binary, conf_dir]:
        if not pathlib.Path(path).exists():
            hub.log.error(f"The path {path} does not exist")
            return False

    checksum_items = []
    with tempfile.TemporaryDirectory() as dirpath:
        if tarfile.is_tarfile(binary):
            with tarfile.open(binary, "r") as tar_fp:
                tar_fp.extractall(dirpath)
                for _fp in pathlib.Path(dirpath).rglob("*"):
                    if _fp.is_file() and _fp.suffix != ".pyc":
                        checksum_items.append(str(_fp))
        elif zipfile.is_zipfile(binary):
            with zipfile.ZipFile(binary) as zip_fp:
                zip_fp.extractall(dirpath)
                for _fp in pathlib.Path(dirpath).rglob("*"):
                    if _fp.is_file() and _fp.suffix != ".pyc":
                        checksum_items.append(str(_fp))

        # generate checksum data for the contents of the binary
        binary_checksum = hub.artifact.init.checksum(checksum_items)
        with open(checksum_file, "w") as fp:
            for _hash, _file in binary_checksum.items():
                fp.write(f"{_hash} {pathlib.Path(*_file.parts[3:])}\n")

    # generate checksum data for files outside of the binary
    # including the salt config file and the binary itself
    copy_items = [binary, str(conf_dir.parent)]
    if files:
        copy_items = copy_items + files

    checksum = hub.artifact.init.checksum(copy_items)
    with open(checksum_file, "a") as fp:
        for _hash, _file in checksum.items():
            fcontent = pathlib.Path(
                *_file.parts[len(pathlib.Path(artifacts_dir).parts) :]
            )
            if str(conf_dir) in str(_file):
                fcontent = pathlib.Path(
                    *_file.parts[len(pathlib.Path(conf_dir.parent.parent).parts) :]
                )
            fp.write(
                "{} {}\n".format(
                    _hash,
                    fcontent,
                )
            )
    return checksum_file


async def extract_binary(
    hub, target_name, tunnel_plugin, binary, binary_path, run_dir, target_os="linux"
):
    """
    extract the binary on the target
    """
    binary_path = str(binary_path)
    artifacts_dir = hub.tool.artifacts.get_artifact_dir(target_os=target_os)
    if not hub.tool.path.clean_path(artifacts_dir, binary):
        hub.log.error(f"The {binary} is not in the correct directory")
        return False

    if not hub.tool.path.clean_path(run_dir, binary_path):
        hub.log.error(f"The {artifact} is not in the correct directory")
        return False

    is_windows = target_os == "windows"
    ret = await hub.artifact.init.extract(
        target_name,
        tunnel_plugin=tunnel_plugin,
        binary=binary,
        run_dir=run_dir,
        target_os=target_os,
    )

    if is_windows:
        # Everyone (WD) has read and execute
        # System (SY) and Administrators (BA) have Full Control
        sddl = "'D:PAI(A;OICI;0x1200a9;;;WD)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)'"
        owner = r"[System.Security.Principal.NTAccount]'BUILTIN\Administrators'"
        cmd = (
            "powershell -command "
            + '"'
            + "; ".join(
                [
                    f'$acl = Get-Acl "{binary_path}"',
                    f'$acl.SetSecurityDescriptorSddlForm("{sddl}")',
                    f"$acl.SetOwner({owner})",
                    f'Set-Acl -Path "{binary_path}" -AclObject $acl',
                ]
            )
            + '"'
        )
    else:
        cmd = f"chmod 744 {binary_path}"
    ret = await hub.tunnel[tunnel_plugin].cmd(target_name, cmd, target_os=target_os)
    if ret.returncode != 0:
        hub.log.error(f"Could not set correct permissions on {binary} for the target")
        return False
    return True
