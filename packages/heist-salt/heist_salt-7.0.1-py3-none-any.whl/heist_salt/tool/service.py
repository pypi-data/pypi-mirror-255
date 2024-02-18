def valid_run_cmd(hub, run_cmd, run_dir=None, target_os="linux", **kwargs):
    """
    function to validate the run_cmd input
    """
    path_sep = "/"
    if target_os == "windows":
        path_sep = "\\"
    run_cmd = run_cmd.split()
    binary = run_cmd[0]
    service_arg = binary.split(path_sep)[-1]
    config_arg = run_cmd[1]
    config = run_cmd[2]

    # validate binary path
    if not hub.tool.path.clean_path(run_dir, binary):
        hub.log.error(f"Binary path {binary} is not a valid path")
        return False

    if service_arg not in (
        "minion",
        "salt-minion",
        "salt",
        "salt-master",
        "master",
        "proxy",
        "salt-proxy",
    ):
        hub.log.error(f"Service arg {service_arg} is not valid")
        return False
    if not config_arg == "-c":
        hub.log.error(f"Wrong config arg settings {config_arg} for the binary")
        return False

    if not hub.tool.path.clean_path(run_dir, config):
        hub.log.error(f"Config path {config}  is not a valid path")
        return False
    return True
