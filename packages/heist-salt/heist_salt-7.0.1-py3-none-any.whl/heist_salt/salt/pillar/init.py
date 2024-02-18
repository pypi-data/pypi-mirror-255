import copy
import pathlib

import salt.config
import salt.utils.yaml
import yaml


def generate_top(hub, target_id, pillar_roots, pillar_env="base"):
    # check top file
    top_file = pillar_roots / "top.sls"
    top_data = {pillar_env: {target_id: [target_id]}}
    if top_file.is_file():
        with open(top_file) as fp:
            top_data = yaml.safe_load(fp)

        if not top_data:
            pass
        else:
            for key in top_data.keys():
                if target_id in top_data[key]:
                    break
                top_data[key].update({target_id: [target_id]})
                with open(top_file, "w") as fp:
                    yaml.safe_dump(top_data, fp)
            return True
    with open(top_file, "w") as fp:
        yaml.safe_dump(top_data, fp)
    return True


def generate_pillar(hub, target_id, data=None):
    """
    Automatically generate pillar on the master.
    """
    opts = salt.config.client_config(hub.salt.key.local_master.DEFAULT_MASTER_CONFIG)
    pillar_env = opts["pillarenv"] or "base"
    pillar_roots = pathlib.Path(opts["pillar_roots"][pillar_env][0])
    pillar_file = pillar_roots / f"{target_id}.sls"
    data = copy.copy(data)
    # check if the data is already in the pillar file
    file_data = None
    if pillar_file.is_file():
        with open(pillar_file) as fp:
            file_data = yaml.safe_load(fp)

    if file_data != data:
        with open(pillar_file, "w") as fp:
            yaml.dump(data, fp)

    hub.salt.pillar.init.generate_top(target_id, pillar_roots, pillar_env=pillar_env)
    return True
