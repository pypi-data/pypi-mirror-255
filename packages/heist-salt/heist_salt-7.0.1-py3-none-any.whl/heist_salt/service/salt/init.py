import tempfile
import textwrap


async def apply_service_config(
    hub,
    target_name,
    tunnel_plugin,
    run_dir,
    service_plugin=None,
    target_os="linux",
    run_dir_root=None,
):
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")

    if not service_plugin:
        service_plugin = hub.service.init.get_service_plugin()

    await getattr(hub, f"service.salt.init.{service_plugin}_conf")(
        target_name,
        tunnel_plugin,
        run_dir,
        target_os=target_os,
        run_dir_root=run_dir_root,
    )


async def systemd_conf(
    hub,
    target_name,
    tunnel_plugin,
    run_dir,
    run_dir_root=None,
    target_os="linux",
):
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")
    binary_path = hub.tool.artifacts.get_salt_path(
        run_dir, run_dir_root=run_dir_root, target_os=target_os
    )
    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        hub.log.error(f"The {run_dir} directory is not valid")
        return False
    salt_pkg = hub.SUBPARSER.split(".")[1]
    contents = textwrap.dedent(
        """\
                [Unit]
                Description=The Salt {salt_pkg}
                Documentation=man:salt-{salt_pkg}(1) file:///usr/share/doc/salt/html/contents.html https://docs.saltproject.io/en/latest/contents.html
                After=network.target salt-master.service

                [Service]
                KillMode=process
                Type=notify
                NotifyAccess=all
                LimitNOFILE=8192
                ExecStart={binary_path}/salt-{salt_pkg} --config-dir {conf} --pid-file={pfile}

                [Install]
                WantedBy=multi-user.target
                """
    )
    _, path = tempfile.mkstemp()
    with open(path, "w+") as wfp:
        wfp.write(
            contents.format(
                binary_path=binary_path,
                conf=hub.tool.path.path_convert("linux", run_dir, ["root_dir", "conf"]),
                pfile=hub.tool.path.path_convert("linux", run_dir, ["pfile"]),
                salt_pkg=salt_pkg,
            )
        )
    salt_pkg = hub.SUBPARSER.split(".")[1]
    await hub.tunnel[tunnel_plugin].send(
        target_name,
        path,
        hub.service.init.service_conf_path(f"salt-{salt_pkg}", "systemd"),
    )

    await hub.tunnel[tunnel_plugin].cmd(target_name, f"systemctl daemon-reload")


async def raw_conf(
    hub, tunnel_plugin, target_name, run_dir, target_os="linux", run_dir_root=None
):
    pass


async def win_service_conf(
    hub, tunnel_plugin, target_name, run_dir, target_os="windows", run_dir_root=None
):
    """
    Install the salt service on Windows using SSM.exe.

    Args:
        tunnel_plugin (str): The tunnel plugin to use
        target_name (str): The name of the target
        run_dir (str): The location of the run_dir
        target_os (str): The target operating system
    """
    if not run_dir_root:
        hub.heist.init.default(target_os, "run_dir_root")
    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        hub.log.error(f"The {run_dir} directory is not valid")
        return False
    # ssm commands
    binary_path = hub.tool.artifacts.get_salt_path(
        run_dir, run_dir_root=run_dir_root, target_os=target_os
    )
    ssm_bin = run_dir / "salt" / "ssm.exe"
    salt_pkg = hub.SUBPARSER.split(".")[1]
    await hub.tunnel[tunnel_plugin].cmd(
        target_name,
        f"{ssm_bin} install salt-{salt_pkg} {binary_path} {salt_pkg}"
        f'-c "{run_dir / "root_dir" / "conf"}"',
    )
    await hub.tunnel[tunnel_plugin].cmd(
        target_name, f"{ssm_bin} set salt-{salt_pkg} Description Heist Salt {salt_pkg}"
    )
    await hub.tunnel[tunnel_plugin].cmd(
        target_name, f"{ssm_bin} set salt-{salt_pkg} Start SERVICE_AUTO_START"
    )
    await hub.tunnel[tunnel_plugin].cmd(
        target_name, f"{ssm_bin} set salt-{salt_pkg} AppStopMethodConsole 24000"
    )
    await hub.tunnel[tunnel_plugin].cmd(
        target_name, f"{ssm_bin} set salt-{salt_pkg} AppStopMethodWindow 2000"
    )
    await hub.tunnel[tunnel_plugin].cmd(
        target_name, f"{ssm_bin} set salt-{salt_pkg} AppStartDelay 60000"
    )


async def start(
    hub,
    target_name,
    tunnel_plugin,
    service_plugin,
    target_id=None,
    run_dir=None,
    target_os="linux",
    run_dir_root=None,
):
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")
    service_name = hub.heist[hub.SUBPARSER].get_service_name(
        service_plugin, target_os=target_os, start=False
    )
    if not await hub.service[service_plugin].status(
        target_name,
        tunnel_plugin,
        service_name,
        block=False,
        target_os=target_os,
        sudo=False,
    ):
        await hub.service.salt.init.apply_service_config(
            target_name,
            tunnel_plugin,
            run_dir,
            service_plugin,
            target_os=target_os,
            run_dir_root=run_dir_root,
        )

        kwargs = {"target_id": target_id}
        await hub.service[service_plugin].start(
            target_name,
            tunnel_plugin,
            service_name,
            run_cmd=hub.heist[hub.SUBPARSER].raw_run_cmd(
                service_plugin,
                run_dir,
                run_dir_root=run_dir_root,
                target_os=target_os,
                **kwargs,
            ),
            block=False,
            target_os=target_os,
            run_dir=run_dir,
        )

        await hub.service[service_plugin].enable(
            tunnel_plugin, target_name, service_name
        )
