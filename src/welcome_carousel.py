from collections.abc import Callable
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw


class WelcomeCarousel(Adw.ApplicationWindow):
    def __init__(self, app: Adw.Application, ok_button: Callable[[str], None]):
        super().__init__(application=app, title="Welcome to Diurnals!")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(Adw.HeaderBar(css_classes=["flat"]))
        
        self.carousel = Adw.Carousel()

        welcome = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        welcome.append(Gtk.Image.new_from_resource("/")

        box.append(self.carousel)
        self.set_content(box)

