from collections.abc import Callable

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

from src.constants import API_KEY_PATH


class APIKeyDialog(Adw.ApplicationWindow):
    def __init__(self, app: Adw.Application, ok_callback: Callable[[str], None]):
        super().__init__(application=app, title="Enter API Key:")
        self.set_resizable(False)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)
        self.ok_callback = ok_callback
        self.api_entry = Gtk.Entry(vexpand=True, valign=Gtk.Align.CENTER)
        box.append(self.api_entry)

        ok_button = Gtk.Button(label="Okay", hexpand=True)
        ok_button.connect("clicked", self.on_ok)
        cancel_button = Gtk.Button(label="Cancel", hexpand=True)
        cancel_button.connect("clicked", lambda _: self.close())

        buttons = Gtk.Box(spacing=6, margin_top=6)
        buttons.append(ok_button)
        buttons.append(cancel_button)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(Adw.HeaderBar())
        toolbar.add_bottom_bar(buttons)
        toolbar.set_content(box)
        self.set_content(toolbar)
        # box.append(buttons)

    def on_ok(self, _):
        API_KEY_PATH.touch()
        self.ok_callback(self.get_input())
        self.close()

    def get_input(self):
        return self.api_entry.get_text()
