import gi

gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import Gtk
from gi.repository import AyatanaAppIndicator3 as appindicator

class TodoistStatusIcon:
    def __init__(self):
        self.indicator = appindicator.Indicator.new(
            "Todoist Dailies",
            "gammastep-status-on",
            appindicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(Gtk.Menu())

