import asyncio
import pathlib

import salt.config


def accept_minion(hub, minion: str) -> bool:
    return hub.salt.key[hub.OPT.heist.key_plugin].accept_minion(minion)


def delete_minion(hub, minion: str) -> bool:
    return hub.salt.key[hub.OPT.heist.key_plugin].delete_minion(minion)


async def check_pki_dir_empty(
    hub, target_name, tunnel_plugin, key_dir, target_os="linux"
):
    """
    function to check if the pki directory is empty or not
    """
    if target_os == "windows":
        # Returns 0 exitcode if empty
        check_dir = f'powershell -command "$items = Get-ChildItem -Path {key_dir}; exit $items.Count"'
        ret = await hub.tunnel[tunnel_plugin].cmd(target_name, check_dir)
        if ret.returncode != 0:
            hub.log.error(
                "The minion pki directory is not empty. Not generating and accepting a key"
            )
            return False
    else:
        # Returns 0 exitcode if NOT empty
        check_dir = f'[ "$(ls -A {key_dir})" ]'
        ret = await hub.tunnel[tunnel_plugin].cmd(target_name, check_dir)
        if ret.returncode == 0:
            hub.log.error(
                "The minion pki directory is not empty. Not generating and accepting a key"
            )
            return False
    return True


async def generate_keys(
    hub,
    target_name,
    tunnel_plugin,
    run_dir,
    run_dir_root=None,
    user=None,
    target_id=None,
    target_os="linux",
):
    minion_type = hub.SUBPARSER.split(".")[1]
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")

    binary_path = str(
        hub.tool.artifacts.get_salt_path(
            run_dir, run_dir_root=run_dir_root, target_os=target_os
        )
    )
    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        hub.log.error(
            f"The path {run_dir} is not valid when attempting to generate keys"
        )
        return False
    is_windows = target_os == "windows"

    if is_windows:
        key_dir = run_dir / "root_dir" / "conf" / "pki" / minion_type
    else:
        key_dir = run_dir / "root_dir" / "etc" / "salt" / "pki" / minion_type

    hub.log.debug(f"Create and secure pki dir and parent directores: {key_dir}")
    if target_os == "windows":
        # Owner (OW), System (SY), and Administrators (BA) have Full Control
        sddl = "'D:PAI(A;OICI;FA;;;OW)(A;OICI;FA;;;SY)(A;OICI;FA;;;BA)'"
        owner = r"[System.Security.Principal.NTAccount]'BUILTIN\Administrators'"
        cmd = "; ".join(
            [
                f'powershell -command "New-Item -Path "{key_dir}" -Type Directory',
                f'$acl = Get-Acl "{key_dir.parent}"',
                f'$acl.SetSecurityDescriptorSddlForm("{sddl}")',
                f"$acl.SetOwner({owner})",
                f'Set-Acl -Path "{key_dir.parent}" -AclObject $acl"',
            ]
        )
    else:
        # mkdir will not add the correct permissions to the parent directories
        # unless each directory is specified
        perms = 0o710 if hub.tunnel.asyncssh.CONS[target_name].get("sudo") else 0o700
        cmd = f"mkdir -m{perms:o} -p {key_dir.parent.parent.parent} {key_dir.parent.parent} {key_dir.parent} {key_dir}"

    ret = await hub.tunnel[tunnel_plugin].cmd(target_name, cmd, target_os=target_os)

    if not is_windows and user:
        await hub.tunnel[tunnel_plugin].cmd(
            target_name,
            f"chown -R {user}:{user} {key_dir.parent.parent.parent}",
        )

    hub.log.debug("Making sure the PKI directory is empty")
    if not await hub.salt.key.init.check_pki_dir_empty(
        target_name, tunnel_plugin, key_dir, target_os=target_os
    ):
        return False

    hub.log.debug(f"Generating {minion_type} keys: {key_dir}")
    cmd = f"{binary_path}/salt-call --local --config-dir {run_dir / 'root_dir' / 'conf'} seed.mkconfig tmp={key_dir}"
    ret = await hub.tunnel[tunnel_plugin].cmd(target_name, cmd, target_os=target_os)
    if ret.returncode != 0:
        hub.log.error("Failed to generate {minion_type} keys")
        return False

    hub.log.debug(f"Copying {minion_type} keys to the master")
    opts = salt.config.client_config(hub.salt.key.local_master.DEFAULT_MASTER_CONFIG)
    minion_key = pathlib.Path(opts["pki_dir"]) / "minions" / target_id

    await hub.tunnel[tunnel_plugin].get(
        target_name,
        key_dir / f"minion.pub",
        minion_key,
    )
    if not minion_key.is_file():
        hub.log.error(f"The {minion_type} key was not accepted")
        return False

    hub.heist.CONS[target_name].update(
        {
            "target_id": target_id,
        }
    )
    hub.log.info(f"Accepted {minion_type} keys for {target_id}")
    return True


async def accept_key_master(
    hub, target_name, tunnel_plugin, run_dir, target_id=None, run_dir_root=False
):
    """
    Accept the minions key on the salt-master
    """
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")
    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        err_msg = f"The run_dir {run_dir} is not a valid path"
        hub.log.error(err_msg)
        return {
            "result": "Error",
            "comment": err_msg,
            "retvalue": 1,
            "target": minion_id,
        }
    if not target_id:
        hub.log.info("Querying minion id and attempting to accept the minion's key")
        ret = await hub.salt.call.init.get_id(
            target_name, tunnel_plugin, run_dir, run_dir_root
        )
        if ret.returncode == 0:
            target_id = ret.stdout.split()[1]
        else:
            hub.log.error("Could not determine the target_id")
            return False
    retry_key_count = hub.OPT.heist.get("retry_key_count", 5)
    while retry_key_count > 0:
        if hub.salt.key.init.accept_minion(target_id):
            break
        await asyncio.sleep(5)
        retry_key_count = retry_key_count - 1
    else:
        hub.log.error(f"Could not accept the key for the minion: {target_id}")
        return False
    hub.heist.CONS[target_name].update(
        {
            "target_id": target_id,
        }
    )
    hub.log.info(f"Accepted the key for minion: {target_id}")
    return True
