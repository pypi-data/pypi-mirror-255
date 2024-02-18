import asyncio
import copy
import pathlib
import secrets
import sys
from typing import Any

import asyncssh
from packaging.version import Version


def __init__(hub):
    for dyne in ("salt", "tool"):
        hub.pop.sub.add(dyne_name=dyne)
    hub.pop.sub.load_subdirs(hub.salt, recurse=True)


def check_deps(hub):
    """
    Function to check required dependencies
    for the Salt Heist manager
    """
    HAS_SALT = None
    try:
        pass

        HAS_SALT = True
    except ImportError:
        HAS_SALT = False

    if not HAS_SALT:
        ret = [
            {
                "result": "Error",
                "comment": "Salt is not installed. Heist-Salt requires Salt.",
                "retvalue": 2,
            }
        ]
        hub.log.debug(f"return value: {ret}")
        return ret
    return True


async def run(
    hub,
    remotes: dict[str, dict[str, str]],
    artifact_version=None,
    manage_service=None,
    **kwargs,
):
    deps = hub.heist.salt.init.check_deps()
    if deps is not True:
        return deps

    coros = []
    ret = [{"result": "Success", "comment": "No problems encountered", "retvalue": 0}]
    clean = kwargs.get("clean", False)
    for id_, remote in remotes.items():
        coro = hub.heist.salt.init.single(
            remote,
            artifact_version=artifact_version,
            manage_service=manage_service,
            clean=clean,
        )
        coros.append(coro)
    async_kwargs = {"return_exceptions": False}
    if sys.version_info == (3, 6):
        async_kwargs["loop"] = hub.pop.Loop
    try:
        ret = await asyncio.gather(*coros, **async_kwargs)
    except OSError as err:
        ret = [{"result": "Error", "comment": f"OS error: {err}", "retvalue": 1}]
    except ValueError:
        ret = [
            {
                "result": "Error",
                "comment": "a Value of unknown type was encountered",
                "retvalue": 2,
            }
        ]

    for _ret in ret:
        hub.log.debug(f"return value: {_ret}")
    return ret


async def single(
    hub,
    remote: dict[str, Any],
    artifact_version=None,
    manage_service=None,
    clean=False,
    **kwargs,
):
    """
    Execute a single async connection
    """
    # create tunnel
    target_name = secrets.token_hex()
    hub.heist.ROSTERS[target_name] = hub.pop.data.imap(copy.copy(remote))
    tunnel_plugin = remote.get("tunnel", "asyncssh")
    target_id = remote.get("id")
    bootstrap = remote.get("bootstrap", False)
    run_dir_root = remote.get("run_dir_root", False)
    pillar_data = remote.get("pillar", False)

    hub.log.debug("Creating SSH Tunnel")
    if not await hub.heist.salt.init.manage_tunnel(
        target_name, tunnel_plugin, remote=remote, bootstrap=bootstrap
    ):
        return {
            "result": "Error",
            "comment": f"Could not establish tunnel with {target_id}",
            "retvalue": 1,
            "target": target_id,
        }

    hub.log.debug("Detecting target os and arch")
    target_os, target_os_arch = await hub.tool.system.os_arch(
        target_name, tunnel_plugin
    )
    if target_os == "windows" and hub.SUBPARSER in ("salt.master", "salt.proxy"):
        salt_pkg = " ".join(hub.SUBPARSER.split("."))
        return {
            "result": "Error",
            "comment": f"{salt_pkg} is not supported on windows. Will not deploy {salt_pkg} to {target_id}",
            "retvalue": 1,
            "target": target_id,
        }

    hub.log.debug(f"Found target_os: {target_os}")

    artifacts_dir = hub.tool.artifacts.get_artifact_dir(target_os=target_os)

    if not hub.OPT.heist.offline_mode:
        salt_repo_url = hub.OPT.heist.salt_repo_url + "onedir/"
        repo_data = await hub.artifact.salt.repo_data(salt_repo_url)
        if isinstance(repo_data, dict) and not artifact_version:
            latest = repo_data.get("latest")
            if latest:
                artifact_version = repo_data["latest"][next(iter(latest))]["version"]
            else:
                artifact_version = max(repo_data.keys(), key=lambda x: Version(x))

        if artifact_version:
            hub.log.debug(f"Getting artifact for {target_os}")
            if not await hub.artifact.init.get(
                "salt",
                target_os=target_os,
                version=artifact_version,
                repo_data=repo_data,
                salt_repo_url=salt_repo_url,
                artifacts_dir=pathlib.Path(artifacts_dir),
            ):
                return {
                    "result": "Error",
                    "comment": "Could not download the artifact",
                    "retvalue": 1,
                    "target": target_id,
                }

    # Get salt user
    user = remote.get("username")
    if not user:
        user = hub.heist.init.default(target_os, "user")
    hub.log.debug(f"Using remote user: {user}")

    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")
    run_dir = hub.tool.path.path_convert(
        target_os,
        run_dir_root,
        ([f"heist_{user}", f"{secrets.token_hex()[:4]}"]),
    )
    hub.log.debug(f"Validating path: {run_dir}")
    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        err_msg = f"The run_dir {run_dir} is not a valid path"
        hub.log.error(err_msg)
        return {
            "result": "Error",
            "comment": err_msg,
            "retvalue": 1,
            "target": target_id,
        }

    # Deploy
    suffix = hub.tool.artifacts.get_artifact_suffix(target_os=target_os)
    binary = hub.artifact.salt.latest(
        "salt", version=artifact_version, suffix=suffix, target_os=target_os
    )
    hub.log.debug(f"Deploying artifact: {binary}")

    run_dir, binary_path, use_prev, prev_artifact = await hub.artifact.init.deploy(
        target_name,
        tunnel_plugin,
        run_dir,
        binary,
        run_dir_root=run_dir_root,
        artifact_name="salt",
        user=user,
        target_os=target_os,
        target_id=target_id,
        bootstrap=bootstrap,
    )

    hub.log.debug("Getting target grains")
    grains = None
    if hub.OPT.heist.auto_service:
        grains = await hub.salt.call.init.get_grains(
            target_name,
            tunnel_plugin,
            run_dir,
            run_dir_root=run_dir_root,
            target_os=target_os,
        )
    hub.log.debug("Getting target grains complete")

    # Don't log out {remote} as it contains SSH password
    hub.log.debug("Getting service plugin")
    service_plugin = hub.service.init.get_service_plugin(remote, grains=grains)
    hub.log.debug(f"Found service plugin: {service_plugin}")

    if manage_service:
        if not prev_artifact or not use_prev:
            err_msg = f"Cannot manage the service, previous artifact never deployed"
            return {
                "result": "Error",
                "comment": err_msg,
                "retvalue": 1,
                "target": target_id,
            }

        return await hub.heist.salt.init.manage_service(
            target_name,
            tunnel_plugin,
            service_plugin,
            manage_service,
            target_id=target_id,
            run_dir=run_dir,
            target_os=target_os,
        )

    hub.heist.CONS[target_name] = {"run_dir": run_dir}
    if not binary_path:
        err_msg = f"Could not deploy the artifact to the target {target_id}"
        hub.log.error(err_msg)
        return {
            "result": "Error",
            "comment": err_msg,
            "retvalue": 1,
            "target": target_id,
        }

    hub.heist.CONS[target_name].update(
        {
            "tunnel_plugin": tunnel_plugin,
            "manager": hub.SUBPARSER,
            "service_plugin": service_plugin,
            "target_os": target_os,
            "target_os_arch": target_os_arch,
        }
    )

    if clean:
        # Clean the target before
        if not use_prev:
            hub.log.error(
                f"Previous artifact not deployed to target {target_id}. Will not clean target"
            )
        else:
            ret = await hub.heist.salt.init.clean(
                target_name,
                tunnel_plugin,
                service_plugin=service_plugin,
                vals={"target_os": target_os},
            )
            use_prev = False
            (
                run_dir,
                binary_path,
                use_prev,
                prev_artifact,
            ) = await hub.artifact.init.deploy(
                target_name,
                tunnel_plugin,
                run_dir,
                binary,
                run_dir_root=run_dir_root,
                artifact_name="salt",
                user=user,
                target_os=target_os,
                target_id=target_id,
                bootstrap=bootstrap,
            )

    if use_prev:
        # Check if we need to upgrade the previous binary
        if hub.OPT.heist.dynamic_upgrade:
            latest = hub.artifact.salt.latest("salt", target_os=target_os)
            if pathlib.Path(latest).name != prev_artifact:
                old_binary = str(pathlib.Path(artifacts_dir) / prev_artifact)
                binary = latest
                await hub.artifact.salt.update(
                    target_name,
                    tunnel_plugin,
                    service_plugin,
                    run_dir,
                    target_id,
                    run_dir_root=run_dir_root,
                    old_binary=old_binary,
                    new_binary=binary,
                    binary_path=binary_path,
                    target_os=target_os,
                )

    hub.log.debug(f"Getting opts use for Salt {hub.SUBPARSER} config")
    _, salt_conf = hub.heist[hub.SUBPARSER].get_salt_opts(
        run_dir=run_dir,
        run_dir_root=run_dir_root,
        target_name=target_name,
        target_os=target_os,
        target_id=target_id,
        bootstrap=bootstrap,
    )
    hub.log.debug("Getting Salt opts for config complete")

    hub.log.debug(f"Connecting to {target_name}")
    if not await hub.heist.salt.init.manage_tunnel(
        target_name,
        tunnel_plugin,
        create=False,
        tunnel=True,
        salt_conf=salt_conf,
        bootstrap=bootstrap,
    ):
        err_msg = f"Failed to connect to {target_name}"
        hub.log.error(err_msg)
        return {
            "result": "Error",
            "comment": err_msg,
            "retvalue": 1,
            "target": target_id,
        }

    salt_pkg = hub.SUBPARSER.split(".")[1]
    if not use_prev:
        # generate keys
        if hub.OPT.heist.generate_keys and not bootstrap and salt_pkg != "master":
            hub.log.debug(f"Generating keys for {target_name}")
            await hub.salt.key.init.generate_keys(
                target_name,
                tunnel_plugin,
                run_dir,
                run_dir_root=run_dir_root,
                user=user,
                target_id=target_id,
                target_os=target_os,
            )

    # Generate pillar data
    if pillar_data:
        hub.salt.pillar.init.generate_pillar(target_id=target_id, data=pillar_data)

    # Start service
    hub.log.debug(f"Starting the service for {hub.SUBPARSER}")
    hub.log.debug(f"Target '{remote.id}' is using service plugin: {service_plugin}")
    await hub.service.salt.init.start(
        target_name,
        tunnel_plugin,
        service_plugin,
        target_id=target_id,
        run_dir=run_dir,
        run_dir_root=run_dir_root,
        target_os=target_os,
    )

    if bootstrap:
        return {
            "result": "Success",
            "comment": f"The target {target_id} bootstrapped Salt {salt_pkg} successfully",
            "retvalue": 0,
            "target": target_id,
        }

    hub.log.debug(
        f"Starting infinite loop on {remote.id}. "
        f"Checkin time: {hub.OPT.heist.checkin_time}"
    )

    while True:
        if not hub.tunnel[tunnel_plugin].connected(target_name):
            # we lost connection, lets check again to see if we can connect
            hub.log.error(f"Lost connection to {target_id}, trying to reconnect")
            if await hub.heist.salt.init.manage_tunnel(
                target_name,
                tunnel_plugin,
                remote=remote,
                create=True,
                tunnel=True,
                reconnect=True,
                salt_conf=salt_conf,
            ):
                hub.log.info(f"Reconnected to {target_id} successfully.")
            else:
                hub.log.error(f"Could not connect to {target_id}")

        await asyncio.sleep(hub.OPT.heist.checkin_time)
        if hub.OPT.heist.dynamic_upgrade:
            latest = hub.artifact.salt.latest("salt", target_os=target_os)
            if latest != binary:
                old_binary = binary
                binary = latest
                await hub.artifact.salt.update(
                    target_name,
                    tunnel_plugin,
                    service_plugin,
                    run_dir,
                    target_id,
                    run_dir_root=run_dir_root,
                    old_binary=old_binary,
                    new_binary=binary,
                    binary_path=binary_path,
                    target_os=target_os,
                )


async def clean(hub, target_name, tunnel_plugin, service_plugin=None, vals=None):
    """
    Clean up the connections
    """
    # clean up service files
    try:
        await hub.service.init.clean(
            target_name,
            tunnel_plugin,
            hub.heist[hub.SUBPARSER].get_service_name(
                service_plugin, target_os=vals["target_os"], start=False
            ),
            service_plugin,
            target_os=vals["target_os"],
        )
    except ValueError:
        hub.log.warning(f"Error during cleanup service files")
    except asyncssh.misc.ChannelOpenError as err:
        hub.log.warning(f"SSH Channel close unexpectedly")
    # clean up run directory and artifact
    try:
        await hub.artifact.init.clean(target_name, tunnel_plugin)
    except asyncssh.misc.ChannelOpenError as err:
        hub.log.warning(f"SSH Channel close unexpectedly")
    except ValueError:
        hub.log.warning(f"Error during cleanup of artifact")


async def manage_tunnel(
    hub,
    target_name,
    tunnel_plugin,
    remote=None,
    create=True,
    tunnel=False,
    reconnect=False,
    salt_conf=None,
    bootstrap=False,
):
    # Create tunnel back to master
    if create:
        hub.log.debug(f'Connecting to host: {remote.get("id")}')
        created = await hub.tunnel[tunnel_plugin].create(
            target_name, remote, reconnect=reconnect
        )
        if not created:
            hub.log.error(f'Connection to host {remote.get("id")} failed')
            return False

        hub.log.info(f'Connection to host {remote.get("id")} success')

    if tunnel and not bootstrap:
        return await hub.heist[hub.SUBPARSER].tunnel_to_ports(
            target_name, tunnel_plugin, salt_conf
        )
    return True


async def manage_service(
    hub,
    target_name,
    tunnel_plugin,
    service_plugin,
    manage_service,
    target_id=None,
    run_dir=None,
    target_os="linux",
):
    """
    Function to help run various service
    commands for the salt service
    """
    if not hub.tool.path.clean_path(
        hub.heist.init.default(target_os, "run_dir_root"), run_dir
    ):
        err_msg = f"The run_dir {run_dir} is not a valid path"
        hub.log.error(err_msg)
        return {
            "result": "Error",
            "comment": err_msg,
            "retvalue": 1,
            "target": target_id,
        }

    service_name = hub.heist[hub.SUBPARSER].get_service_name(
        service_plugin, target_os=target_os, start=False
    )
    kwargs = {}
    for opt_kwarg in ["run_dir", "run_cmd"]:
        if (
            opt_kwarg
            in hub.service[service_plugin][manage_service].signature.parameters.keys()
        ):
            if opt_kwarg == "run_dir":
                kwargs[opt_kwarg] = run_dir
            elif opt_kwarg == "run_cmd":
                kwargs[opt_kwarg] = hub.heist[hub.SUBPARSER].raw_run_cmd(
                    service_plugin, run_dir, target_os
                )
    service = await hub.service[service_plugin][manage_service](
        target_name,
        tunnel_plugin,
        service=service_name,
        target_os=target_os,
        **kwargs,
    )
    err_msg = f"Could not {manage_service} the service {service_name}"
    msg = (
        f"The service {service_name} was succesfully put into status {manage_service}. Closing Heist connection.",
    )
    if manage_service == "status":
        msg = f"Service {service_name} is started"
        err_msg = f"Service {service_name} is not started"

    if not service:
        return {
            "result": "Error",
            "comment": err_msg,
            "retvalue": 1,
            "target": target_id,
        }

    return {
        "result": "Success",
        "comment": msg,
        "retvalue": 0,
        "target": target_id,
    }
