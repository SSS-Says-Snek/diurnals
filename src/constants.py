import pathlib

import gi

gi.require_version("GLib", "2.0")
from gi.repository import GLib

APPLICATION_ID = "@APP_ID@"
CONFIG_PATH = pathlib.Path(GLib.get_user_config_dir()) / "todoist-dailies.conf"
API_KEY_PATH = pathlib.Path(GLib.get_user_config_dir()) / ".todoist-dailies.env"
