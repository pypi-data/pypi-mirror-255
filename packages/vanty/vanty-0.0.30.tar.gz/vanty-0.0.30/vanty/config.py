# Copyright
# Extended by Advantch.com 2023
# Attribution: Modal Labs 2022
import logging
import os
import typing
import warnings

import toml

# Locate config file and read it

user_config_path: str = os.environ.get("VANTY_CONFIG_PATH") or os.path.expanduser(
    "~/.vanty.toml"
)


def _read_user_config():
    if os.path.exists(user_config_path):
        with open(user_config_path) as f:
            return toml.load(f)
    else:
        return {}


_user_config = _read_user_config()


def config_profiles():
    """List the available vanty profiles in the .vanty.toml file."""
    return _user_config.keys()


def _config_active_profile():
    for key, values in _user_config.items():
        if values.get("active", False) is True:
            return key
    else:
        return "default"


def config_set_active_profile(env: str):
    """Set the user's active vanty profile by writing it to the `.vanty.toml` file."""
    if env not in _user_config:
        raise KeyError(env)

    for key, values in _user_config.items():
        values.pop("active", None)

    _user_config[env]["active"] = True
    _write_user_config(_user_config)


_profile = os.environ.get("VANTY_PROFILE", _config_active_profile())


class _Setting(typing.NamedTuple):
    default: typing.Any = None
    transform: typing.Callable[[str], typing.Any] = lambda x: x  # noqa: E731


_SETTINGS = {
    "loglevel": _Setting("WARNING", lambda s: s.upper()),
    "server_url": _Setting(default="https://www.advantch.com/api/v1"),
    "token_id": _Setting(),
    "local_folder": _Setting(default=".", transform=os.path.abspath),
    "token_secret": _Setting(),
    "ssr_enabled": _Setting(default=False, transform=lambda s: s.lower() == "true"),
    "package_manager": _Setting(default="pnpm"),
    "core_service_name": _Setting(default="django"),
    "worker_service_name": _Setting(default="worker"),
    "cache_service_name": _Setting(default="redis"),
}


class Config:
    """Singleton that holds configuration used by Vanty internally."""

    def __init__(self):
        pass

    def get(self, key, profile=None):
        """Looks up a configuration value.

        Will check (in decreasing order of priority):
        1. Any environment variable of the form VANTY_FOO_BAR
        2. Settings in the user's .toml configuration file
        3. The default value of the setting
        """
        if profile is None:
            profile = _profile
        s = _SETTINGS[key]
        env_var_key = "VANTY_" + key.upper()
        if env_var_key in os.environ:
            return s.transform(os.environ[env_var_key])
        elif profile in _user_config and key in _user_config[profile]:
            return s.transform(_user_config[profile][key])
        else:
            return s.default

    def __getitem__(self, key):
        return self.get(key)
    
    def display(self):
        return {key: self.get(key) for key in _SETTINGS.keys()}

    def __repr__(self):
        return repr({key: self.get(key) for key in _SETTINGS.keys()})


config = Config()

# Logging

logger = logging.getLogger("vanty-cli")
ch = logging.StreamHandler()
log_level_numeric = logging.getLevelName(config["loglevel"])
logger.setLevel(log_level_numeric)
ch.setLevel(log_level_numeric)
ch.setFormatter(
    logging.Formatter("%(asctime)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z")
)
logger.addHandler(ch)

# Utils to write config


def _store_user_config(new_settings, profile=None):
    """Internal method, used by the CLI to set tokens."""
    if profile is None:
        profile = _profile
    user_config = _read_user_config()
    user_config.setdefault(profile, {}).update(**new_settings)
    _write_user_config(user_config)


def _write_user_config(user_config):
    with open(user_config_path, "w") as f:
        toml.dump(user_config, f)


# Make sure all deprecation warnings are shown
# See https://docs.python.org/3/library/warnings.html#overriding-the-default-filter
warnings.filterwarnings(
    "default",
    category=DeprecationWarning,
    module="vanty",
)
