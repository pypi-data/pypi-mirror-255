def get_salt_path(hub, run_dir, run_dir_root=None, target_os="linux"):
    """
    Return the full path to the salt binary.
    """
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")

    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        hub.log.error(
            f"The path {run_dir} is not a valid path when getting the full Salt path."
        )
        return False

    return run_dir / "salt"


def target_conf(hub, run_dir, run_dir_root=None, target_os="linux"):
    """
    Function to return the path of the conf
    directory on the target
    """
    if not run_dir_root:
        run_dir_root = hub.heist.init.default(target_os, "run_dir_root")
    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        hub.log.error(
            f"The path {run_dir} is not a valid path when getting targets config."
        )
        return False

    return run_dir / "root_dir" / "conf"
