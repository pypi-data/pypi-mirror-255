import pathlib

import asyncssh


async def run(
    hub,
    remotes: dict[str, dict[str, str]],
    artifact_version=None,
    manage_service=None,
    **kwargs,
):
    return await hub.heist.salt.init.run(
        remotes,
        artifact_version=artifact_version,
        manage_service=manage_service,
        **kwargs,
    )


async def clean(hub, target_name, tunnel_plugin, service_plugin=None, vals=None):
    """
    Clean up the connections
    """
    await hub.heist.salt.init.clean(
        target_name,
        tunnel_plugin,
        service_plugin,
        vals,
    )
    target_id = hub.heist.CONS[target_name].get("target_id")
    if target_id:
        if not hub.salt.key.init.delete_minion(target_id):
            hub.log.error(f"Could not delete the key for minion: {target_id}")
            return False
    return True


def get_service_name(hub, service_plugin, target_os="linux", start=True):
    """
    Get the service name for the given service

    :param service_plugin:
        The service plugin being used to manage the service.
    :param target_os:
        The OS of the target.
    :param start:
        Return service name when starting the service.
    """
    return "salt-minion"


async def tunnel_to_ports(hub, target_name, tunnel_plugin, salt_conf):
    import salt.config
    import salt.syspaths

    master_opts = salt.config.client_config(
        pathlib.Path(salt.syspaths.CONFIG_DIR) / "master"
    )
    try:
        await hub.tunnel[tunnel_plugin].tunnel(
            target_name,
            salt_conf["publish_port"],
            master_opts.get("publish_port", 4505),
        )
        await hub.tunnel[tunnel_plugin].tunnel(
            target_name,
            salt_conf["master_port"],
            master_opts.get("master_port", 4506),
        )
        hub.log.info(f"Established SSH tunnel with {salt_conf['id']}")
    except asyncssh.misc.ChannelListenError as err:
        hub.log.error(f"Could not establish SSH tunnel with {salt_conf['id']}")
        return False
    except asyncssh.misc.ChannelOpenError as err:
        hub.log.warning(f"SSH Channel closed unexpectedly with {salt_conf['id']}")
        return False
    return True


def generate_aliases(hub, run_dir, run_dir_root=None, target_os="linux"):
    """
    Generate the alias data for the Salt Minion
    """
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")

    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        hub.log.error(
            f"The run_dir {run_dir} is not a valid path when generating aliases"
        )
        return False

    artifacts_dir = (
        pathlib.Path(hub.tool.artifacts.get_artifact_dir(target_os=target_os))
        / "scripts"
        / "minion"
    )
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    aliases = {
        "salt-call": {"file": artifacts_dir / "salt-call", "cmd": "salt-call"},
        "salt-minion": {"file": artifacts_dir / "salt-minion", "cmd": "salt-minion"},
    }

    content = (
        "#!/bin/bash\n"
        'if [[ -z "${{SSL_CERT_DIR}}" ]] && command -v openssl &> /dev/null; then\n'
        "_DIR=$(openssl version -d)\n"
        'export SSL_CERT_DIR=${{_DIR:13:-1}}"/certs"\n'
        'export SSL_CERT_FILE=${{_DIR:13:-1}}"/cert.pem"\n'
        "fi\n"
        f"exec {str(hub.tool.artifacts.get_salt_path(run_dir, run_dir_root=run_dir_root, target_os=target_os))}"
        '/{alias} "${{@:1}}" -c '
        f"{hub.tool.artifacts.target_conf(run_dir, run_dir_root=run_dir_root, target_os=target_os)}"
    )
    if target_os == "windows":
        content = (
            "@ECHO OFF\n"
            f"{str(hub.tool.artifacts.get_salt_path(run_dir, run_dir_root=run_dir_root, target_os=target_os))} "
            "{alias} %* -c "
            f"{hub.tool.artifacts.target_conf(run_dir, run_dir_root=run_dir_root, target_os=target_os)}"
        )
    return aliases, artifacts_dir, content


def get_salt_opts(
    hub,
    run_dir,
    target_name,
    run_dir_root=None,
    target_os="linux",
    target_id=None,
    bootstrap=False,
):
    config = {}
    roster = hub.heist.ROSTERS[target_name]

    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")

    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        hub.log.error(
            f"The run_dir {run_dir} is not a valid path when getting salt opts"
        )
        return False

    required = {
        "root_dir": str(run_dir / "root_dir"),
        "id": target_id,
        "grains": {"minion_type": "heist"},
    }
    if not bootstrap:
        required["master"] = "127.0.0.1"
        required["master_port"] = 44506
        required["publish_port"] = 44505
    minion_opts = roster.get("minion_opts")
    if minion_opts:
        for key, value in minion_opts.items():
            # Use configurations set by user
            config[key] = value

    for req in required.keys():
        if not config.get(req):
            config[req] = required[req]

    return "minion", config


def raw_run_cmd(
    hub, service_plugin, run_dir, run_dir_root=None, target_os="linux", **kwargs
):
    """
    function to return the run_cmd used to start the salt
    minion when using the raw service plugin
    """
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")

    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        hub.log.error(f"The {run_dir} directory is not valid")
        return False

    service_name = hub.heist[hub.SUBPARSER].get_service_name(
        service_plugin, target_os=target_os
    )
    run_cmd = (
        str(
            hub.tool.artifacts.get_salt_path(
                run_dir, run_dir_root=run_dir_root, target_os=target_os
            )
            / service_name
        )
        + f" -c {hub.tool.artifacts.target_conf(run_dir, run_dir_root=run_dir_root, target_os=target_os)}"
    )
    if target_os == "linux":
        run_cmd = run_cmd + " -d"
    return run_cmd
