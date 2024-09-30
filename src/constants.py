import pathlib

import gi

gi.require_version("GLib", "2.0")
from gi.repository import GLib

APPLICATION_ID = "@APP_ID@"
API_KEY_PATH = pathlib.Path(GLib.get_user_config_dir()) / ".diurnals.env"
VERSION = "@VERSION@"

# For developers running dev_main.py. Overwrites stuff temporarily
if APPLICATION_ID == "@APP" + "_ID@":
    APPLICATION_ID = "io.github.sss_says_snek.diurnals"
    VERSION = "0.0.2"
