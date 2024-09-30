from collections.abc import Callable
import gi

from src.constants import API_KEY_PATH

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.main import TodoistDailies

class WelcomeCarousel(Adw.ApplicationWindow):
    def __init__(self, app: "TodoistDailies", finish_callback: Callable[[str], None]):
        super().__init__(application=app, title="Welcome to Diurnals!")

        self.set_default_size(800, 600)

        self.finish_callback = finish_callback

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(Adw.HeaderBar(css_classes=["flat"]))
        
        self.carousel = Adw.Carousel()
        self.carousel.connect("page-changed", self.on_page_changed)
        carousel_dots = Adw.CarouselIndicatorDots(carousel=self.carousel)

        carousel_overlay = Gtk.Overlay(child=self.carousel)
        self.carousel_back = Gtk.Button(icon_name="go-previous-symbolic", css_classes=["circular"], margin_start=12, halign=Gtk.Align.START, valign=Gtk.Align.CENTER, tooltip_text="Previous page")
        self.carousel_next = Gtk.Button(icon_name="go-next-symbolic", css_classes=["circular"], margin_end=12, halign=Gtk.Align.END, valign=Gtk.Align.CENTER, tooltip_text="Next page")
        carousel_overlay.add_overlay(self.carousel_back)
        carousel_overlay.add_overlay(self.carousel_next)

        self.carousel_back.connect("clicked", self.on_back_button)
        self.carousel_next.connect("clicked", self.on_next_button)

        # 1st page: Welcome
        welcome = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True, hexpand=True)
        welcome_status = Adw.StatusPage(title="Welcome to Todoist Dailies!", description="Receive a daily popup to notify about upcoming Todoist tasks.")

        app_icon = Gtk.Image.new_from_resource("/io/github/sss_says_snek/todoist_dailies/images/app_icon.svg")
        app_icon.set_pixel_size(300)
        welcome.append(app_icon)
        welcome.append(welcome_status)

        # 2nd page: API Key
        api_key_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True, hexpand=True)
        api_key_icon = Gtk.Image(icon_name="key-symbolic", pixel_size=270)
        api_key_status = Adw.StatusPage(vexpand=True, hexpand=True, title="Enter your API Key", description=r'Your API key can be found in "Settings" > "Integrations" > "Developer"')
        self.api_entry = Gtk.Entry(vexpand=True, valign=Gtk.Align.CENTER, placeholder_text="Enter your key here")
        api_key_status.set_child(self.api_entry)

        api_key_box.append(api_key_icon)
        api_key_box.append(api_key_status)

        # 3rd and last page: Routines
        routines_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True, hexpand=True)
        routines_icon = Gtk.Image(icon_name="task-due-symbolic", pixel_size=270)
        routines_status = Adw.StatusPage(vexpand=True, hexpand=True, title="Set your routines", description=r'Customize at what days and times the popup shows up under the three dots > "Routines"')
        self.finish_button = Gtk.Button(css_classes=["suggested-action", "pill"], halign=Gtk.Align.CENTER, label="Finish")
        self.finish_button.connect("clicked", self.on_finished)
        routines_status.set_child(self.finish_button)

        routines_box.append(routines_icon)
        routines_box.append(routines_status)

        # Carousel
        self.carousel.append(welcome)
        self.carousel.append(api_key_box)
        self.carousel.append(routines_box)

        box.append(carousel_overlay)
        box.append(carousel_dots)
        self.set_content(box)

        self.on_page_changed() # Call to automatically hide carousel back button

    def on_finished(self, _):
        api_key = self.api_entry.get_text()

        API_KEY_PATH.touch()
        with open(API_KEY_PATH, "w") as w:
            w.write(f"API_KEY={api_key}")

        self.finish_callback(api_key)
        self.close()

    def on_page_changed(self, _=None, index=0):
        if index == 0: # Start
            self.carousel_back.hide()
            self.carousel_next.show()
        elif index == 2: # End
            self.carousel_back.show()
            self.carousel_next.hide()
        else:
            self.carousel_back.show()
            self.carousel_next.show()

    def on_back_button(self, _):
        prev_page = self.carousel.get_nth_page(int(self.carousel.get_position()) - 1)
        self.carousel.scroll_to(prev_page, True)

    def on_next_button(self, _):
        next_page = self.carousel.get_nth_page(int(self.carousel.get_position()) + 1)
        self.carousel.scroll_to(next_page, True)
