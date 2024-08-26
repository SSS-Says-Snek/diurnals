from collections.abc import Callable
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw


class APIKeyDialog(Adw.ApplicationWindow):
    def __init__(self, app: Adw.Application, ok_callback: Callable[[str], None]):
        super().__init__(application=app, title="Enter API Key:")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(Adw.HeaderBar())
        self.set_content(box)

        self.ok_callback = ok_callback
        self.api_entry = Gtk.Entry()
        box.append(self.api_entry)

        ok_button = Gtk.Button(label="Okay", hexpand=True)
        ok_button.connect("clicked", self.on_ok)
        cancel_button = Gtk.Button(label="Cancel", hexpand=True)

        buttons = Gtk.Box(spacing=6, margin_top=6)
        buttons.append(ok_button)
        buttons.append(cancel_button)
        box.append(buttons)

    def on_ok(self, _):
        self.ok_callback(self.get_input())
        self.close()

    def get_input(self):
        return self.api_entry.get_text()
