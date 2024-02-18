import json


async def get_grains(
    hub, target_name, tunnel_plugin, run_dir, target_os="linux", run_dir_root=False
):
    """
    Run grains.items and return the grains as a dictionary.
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
    binary_path = hub.tool.artifacts.get_salt_path(run_dir, target_os=target_os)
    if target_os == "windows":
        pass
    grains = await hub.tunnel[tunnel_plugin].cmd(
        target_name,
        f"{binary_path / 'salt-call'} --config-dir {run_dir / 'root_dir' / 'conf'} "
        f"--local grains.items --out json",
        target_os=target_os,
    )
    _, sep, grains = grains.stdout.partition("{")
    grains = sep + grains
    return json.loads(grains)["local"]


async def get_id(
    hub, target_name, tunnel_plugin, run_dir, target_os="linux", run_dir_root=False
):
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
    binary_path = run_dir / "salt"
    return await hub.tunnel[tunnel_plugin].cmd(
        target_name,
        f"{binary_path} call --config-dir {run_dir} --local grains.get id",
        target_os=target_os,
    )
