# Use a local Salt master's keys to accept a minion key
import contextlib
import os

import salt.config
import salt.key
import salt.syspaths
import salt.version


def __init__(hub):
    hub.salt.key.local_master.DEFAULT_MASTER_CONFIG = os.path.join(
        salt.syspaths.CONFIG_DIR, "master"
    )


def old_salt(hub):
    """
    Query to see if Salt version is < 3003. Versions
    previous to 3003 did not support calling salt.key.get_key
    as a context manager. This function and saltkey_context_mgr
    can be deleted when versions <3003 are no longer supported
    in Salt.
    """
    ver = salt.version.__version__
    if ver < "3003":
        return True
    return False


@contextlib.contextmanager
def saltkey_context_mgr(hub, opts):
    yield salt.key.get_key(opts)


def accept_minion(hub, minion: str) -> bool:
    opts = salt.config.client_config(hub.salt.key.local_master.DEFAULT_MASTER_CONFIG)
    with salt.key.get_key(
        opts
    ) if not hub.salt.key.local_master.old_salt() else hub.salt.key.local_master.saltkey_context_mgr(
        opts
    ) as salt_key:
        if minion not in salt_key.list_status("all")["minions_pre"]:
            return False

        salt_key.accept(
            match=[
                minion,
            ],
            include_denied=False,
            include_rejected=False,
        )

    return minion in salt_key.list_status("accepted")["minions"]


def delete_minion(hub, minion: str) -> bool:
    opts = salt.config.client_config(hub.salt.key.local_master.DEFAULT_MASTER_CONFIG)
    with salt.key.get_key(
        opts
    ) if not hub.salt.key.local_master.old_salt() else hub.salt.key.local_master.saltkey_context_mgr(
        opts
    ) as salt_key:
        if minion not in salt_key.list_status("all")["minions"]:
            hub.log.debug(f"The minion `{minion}` is already denied")
            return True

        salt_key.delete_key(
            match=[
                minion,
            ],
            preserve_minions=None,
            revoke_auth=False,
        )

    return minion not in salt_key.list_status("all")["minions"]
