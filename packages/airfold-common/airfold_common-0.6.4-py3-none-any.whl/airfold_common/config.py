from pathlib import Path

import yaml

from airfold_common.log import log

SPECS_FILE = "specs.yaml"


def parse_specs(data: dict) -> dict[str, dict]:
    return {name: dict(**spec, name=name) for name, spec in data.items()}


def specs_from_path(path: Path) -> dict[str, dict]:
    spec_path: Path = path if path.is_file() else path / SPECS_FILE
    if not spec_path.exists() or not spec_path.is_file():
        log.info("No specs found on disk")
        return {}

    _specs: dict = yaml.safe_load(open(spec_path))

    return parse_specs(_specs)


def merge_dicts(conf_data, env_data):
    for k, v in env_data.items():
        if k in conf_data and isinstance(conf_data[k], dict) and isinstance(env_data[k], dict):  # noqa
            merge_dicts(conf_data[k], env_data[k])
        else:
            conf_data[k] = env_data[k]
