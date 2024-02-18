import pathlib


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
    return await hub.heist.salt.init.clean(
        target_name,
        tunnel_plugin,
        service_plugin,
        vals,
    )


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
    return "salt-master"


async def tunnel_to_ports(hub, target_name, tunnel_plugin, salt_conf):
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
        / "master"
    )
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    aliases = {
        "salt-key": {"file": artifacts_dir / "salt-key", "cmd": "salt-key"},
        "salt": {"file": artifacts_dir / "salt", "cmd": "salt"},
        "salt-master": {"file": artifacts_dir / "salt-master", "cmd": "salt-master"},
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
            f"{str(hub.tool.artifacts.get_salt_path(run_dir, run_dir_root=run_dir_root, target_os=target_os))}"
            "/{alias} %* -c "
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
    }
    master_opts = roster.get("master_opts")
    if master_opts:
        for key, value in master_opts.items():
            # Use configurations set by user
            config[key] = value

    for req in required.keys():
        if not config.get(req):
            config[req] = required[req]

    return "master", config


def raw_run_cmd(
    hub, service_plugin, run_dir, run_dir_root=None, target_os="linux", **kwargs
):
    """
    function to return the run_cmd used to start the Salt
    master when using the raw service plugin
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
        )
        + f"/{service_name}"
        + f" -c {hub.tool.artifacts.target_conf(run_dir, run_dir_root=run_dir_root, target_os=target_os)}"
    )
    if target_os == "linux":
        run_cmd = run_cmd + " -d"
    return run_cmd
