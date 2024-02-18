import yaml


def get_minion_opts(
    hub,
    run_dir,
    target_name,
    target_os="linux",
    target_id=None,
    bootstrap=False,
    run_dir_root=None,
):
    config = {}
    roster = hub.heist.ROSTERS[target_name]
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")
    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        hub.log.error(f"The {run_dir} directory is not valid when generating salt opts")
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

    return config


def mk_config(hub, target_name, config, conf_file):
    """
    Create a config to use with this execution and return the file path
    for said config
    """
    perms = 0o710 if hub.tunnel.asyncssh.CONS[target_name].get("sudo") else 0o700
    if not conf_file.parent.is_dir():
        conf_file.parent.mkdir(mode=perms, parents=True)
    if not conf_file.is_file():
        conf_file.touch(mode=perms)
    with open(conf_file, "w+") as wfp:
        yaml.safe_dump(config, wfp)
    return conf_file
