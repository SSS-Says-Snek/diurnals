import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class APIKeyDialog(Gtk.Dialog):
    def __init__(self, parent): 
        super().__init__(title="Enter API Key:", use_header_bar=True)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        box = self.get_content_area()
        
        self.api_entry = Gtk.Entry()
        box.add(self.api_entry)
        self.show_all()

    def get_input(self):
        return self.api_entry.get_text()
