import gi

gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import Gtk, GObject
from gi.repository import AyatanaAppIndicator3 as appindicator

class TodoistStatusIcon(GObject.GObject):
    __gsignals__ = {
        "quit_item": (GObject.SIGNAL_RUN_FIRST, None, ())
    }


    def __init__(self):
        super().__init__()

        self.indicator = appindicator.Indicator.new(
            "Todoist Dailies",
            "gammastep-status-on",
            appindicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.status_menu = Gtk.Menu()

        quit_item = Gtk.MenuItem.new_with_label("Quit Process")
        quit_item.connect("activate", lambda _: self.emit("quit_item"))
        self.status_menu.append(quit_item)

        self.status_menu.show_all()
        self.indicator.set_menu(self.status_menu)

