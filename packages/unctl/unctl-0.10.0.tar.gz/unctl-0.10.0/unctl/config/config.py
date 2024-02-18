import os
from pydantic import ValidationError
import yaml
import contextvars

from .app_config import AppConfig

DEFAULT_CONFIG_PATH = "~/.config/unctl"


def load_config(config_path: str) -> AppConfig:
    """
    The `load_config` function loads a YAML configuration file and returns an instance
    of the `AppConfig` class.

    :param config_path: The `config_path` parameter is a string that represents the path
    to the YAML configuration file
    :type config_path: str
    :return: The function `load_config` returns an instance of the `AppConfig` class.
    """

    if config_path is not None and not os.path.isfile(config_path):
        raise Exception(f"config file not found by --config path {config_path}")

    # If `config_path` is not specified, then `config_path` fallbacks to the
    # user default configuration file path `~/.config/unctl/config.yaml`.
    if config_path is None:
        config_path = os.path.expanduser(f"{DEFAULT_CONFIG_PATH}/config.yaml")

        # If config file doesn't exist in default path then need create it
        if not os.path.isfile(config_path):
            config_path = os.path.join(os.path.dirname(__file__), "config_default.yaml")

    with open(config_path, "r") as config_file:
        config_data = yaml.safe_load(config_file)

    try:
        return AppConfig(**config_data)
    except ValidationError as e:
        last = e.errors().pop()
        path = ".".join(str(x) for x in last.get("loc"))
        print(
            f"❌ Failed to parse config file. Problem: {last.get('msg')}, path: {path}"
        )
    return AppConfig()


ConfigInstance = contextvars.ContextVar("ConfigInstance", default=None)


def set_config_instance(config_instance):
    ConfigInstance.set(config_instance)


def get_config_instance() -> AppConfig:
    return ConfigInstance.get()
