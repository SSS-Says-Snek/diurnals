"""This only exists because I can only import stuff from the outside :sob:"""

from src import main

pkgdatadir = r"/usr/local/share/diurnals"

import os
import gi

gi.require_version("Gio", "2.0")

from gi.repository import Gio
resource = Gio.Resource.load(os.path.join(pkgdatadir, 'diurnals.gresource'))
resource._register() # type: ignore

main.main()
