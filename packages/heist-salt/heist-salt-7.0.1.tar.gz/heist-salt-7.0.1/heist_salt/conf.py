CLI_CONFIG = {
    # The dyne will always be heist.
    # List the subcommands that will expose this option
    "key_plugin": {"subcommands": ["salt.minion", "salt.master"], "dyne": "heist"},
    "onedir": {"subcommands": ["salt.minion", "salt.master"], "dyne": "heist"},
}
CONFIG = {
    # This will show up in hub.OPT.heist.key_plugin
    "key_plugin": {
        "default": "local_master",
        "help": "Define the salt key plugin to use.",
        "dyne": "heist",
    },
    "generate_keys": {
        "default": True,
        "action": "store_true",
        "help": "Generate the salt minions keys on the minion "
        "and copy over to the master",
        "dyne": "heist",
    },
    "retry_key_count": {
        "default": 5,
        "help": "Amount of times to retry accepting the salt-key,"
        "while the salt minion is still starting up",
        "dyne": "heist",
    },
    "salt_repo_url": {
        "default": "https://repo.saltproject.io/salt/py3/",
        "help": "The url to a repo that contains the repo.json/repo.mp"
        "file and the Salt artifacts",
        "dyne": "heist",
    },
    "offline_mode": {
        "default": False,
        "help": "Do not query a repo for artifacts. Use the artifacts already in the artifact directory.",
        "type": bool,
        "dyne": "heist",
    },
    "onedir": {
        "default": False,
        "type": bool,
        "action": "store_true",
        "help": "Use the onedir package of salt. If False, singlebin will be used.",
        "dyne": "heist",
    },
}

SUBCOMMANDS = {
    "salt.minion": {"help": "", "dyne": "heist"},
    "salt.master": {"help": "", "dyne": "heist"},
    "salt.proxy": {"help": "", "dyne": "heist"},
}
DYNE = {
    "artifact": ["artifact"],
    "heist": ["heist"],
    "salt": ["salt"],
    "service": ["service"],
    "tool": ["tool"],
}
