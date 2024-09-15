from collections.abc import Callable
from configparser import ConfigParser
from datetime import datetime

from gi.repository import Adw, Gtk

from src.constants import CONFIG_PATH


class ScheduleRow(Adw.ActionRow):
    DAY_OPTIONS = [
        "day",
        "weekday",
        "weekend day",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    AM_PM_OPTIONS = ["PM", "AM"]

    def __init__(self, routine_id: str, delete_button_callback: Callable, config: ConfigParser, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = routine_id
        self.config = config

        self.delete_button_callback = delete_button_callback
        self.day_option = Gtk.DropDown.new_from_strings(self.DAY_OPTIONS)
        self.am_pm_option = Gtk.DropDown.new_from_strings(self.AM_PM_OPTIONS)

        self.day_option.connect("notify::selected", self.write_to_config)
        self.am_pm_option.connect("notify::selected", self.write_to_config)

        day_child = self.day_option.get_first_child()
        if day_child is not None:
            day_child.add_css_class("flat")  # There's no flat option for dropdowns :( so here's a workaround

        am_pm_child = self.am_pm_option.get_first_child()
        if am_pm_child is not None:
            am_pm_child.add_css_class("flat")  # Always true, but here for the type hint

        # Box to hold hour, minute, and that goofy ahh colon
        self.hour_option = Gtk.SpinButton(
            css_classes=["flat"],
            orientation=Gtk.Orientation.VERTICAL,
            adjustment=Gtk.Adjustment(value=11, lower=1, upper=12, step_increment=1),
        )
        self.hour_option.connect("output", self.adjust_output)
        self.hour_option.connect("value-changed", self.write_to_config)

        self.minute_option = Gtk.SpinButton(
            css_classes=["flat"],
            orientation=Gtk.Orientation.VERTICAL,
            adjustment=Gtk.Adjustment(value=59, lower=0, upper=59, step_increment=1),
        )
        self.minute_option.connect("output", self.adjust_output)
        self.minute_option.connect("value-changed", self.write_to_config)

        # Delete button
        self.delete_button = Gtk.Button(
            halign=Gtk.Align.END, hexpand=True, valign=Gtk.Align.CENTER, vexpand=False, css_classes=["flat"]
        )
        self.delete_button.connect("clicked", self.delete_callback)
        self.delete_button.set_icon_name("user-trash-symbolic")

        # Syncs config file to widget
        day, time = self.config["Routine"][self.id].split()
        day = day.replace("_", " ")
        time = self.convert_24hr_to_12hr(time)
        hour, minute, am_pm = time.split()

        self.day_option.set_selected(self.DAY_OPTIONS.index(day))
        self.am_pm_option.set_selected(self.AM_PM_OPTIONS.index(am_pm))
        self.hour_option.set_value(int(hour))
        self.minute_option.set_value(int(minute))

        # Adds all elements to box
        box = Gtk.Box(spacing=6, margin_start=12, margin_end=12, margin_top=6, margin_bottom=6)
        box.append(Gtk.Label(label="Activate every"))
        box.append(self.day_option)
        box.append(Gtk.Label(label="at"))
        box.append(self.hour_option)
        box.append(Gtk.Label(label=":"))
        box.append(self.minute_option)
        box.append(self.am_pm_option)
        box.append(self.delete_button)

        self.set_child(box)

    def delete_callback(self, _):
        """Passes itself into the actual callback for the group to delete"""
        self.delete_button_callback(self)

    @staticmethod
    def adjust_output(spin_button: Gtk.SpinButton):
        """Rounds to int and add leading zeroes to SpinButton"""
        adjustment = spin_button.get_adjustment()
        spin_button.set_text(f"{int(adjustment.get_value()):02d}")
        return True

    @staticmethod
    def convert_24hr_to_12hr(time: str):
        input_time = datetime.strptime(time, "%H:%M")
        return datetime.strftime(input_time, "%I %M %p")

    @staticmethod
    def convert_12hr_to_24hr(time: str):
        input_time = datetime.strptime(time, "%I:%M %p")
        return datetime.strftime(input_time, "%H:%M")

    def get_options(self):
        """Extracts options from the UI"""
        result = ""
        day_item = self.day_option.get_selected_item()
        am_pm_item = self.am_pm_option.get_selected_item()

        hour = self.hour_option.get_value_as_int()
        minute = self.minute_option.get_value_as_int()
        if isinstance(day_item, Gtk.StringObject):  # Always true, for the type hint
            result += day_item.get_string().replace(" ", "_") + " "
        if isinstance(am_pm_item, Gtk.StringObject):  # Always true, for the type hint
            am_pm = am_pm_item.get_string()
            result += self.convert_12hr_to_24hr(f"{hour}:{minute} {am_pm}")

        return result

    def write_to_config(self, *_):
        self.config["Routine"][self.id] = self.get_options()
        with open(CONFIG_PATH, "w") as w:
            self.config.write(w)


class ConfigWindow(Adw.PreferencesDialog):
    def __init__(self, config: ConfigParser, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config

        self.set_content_width(1000)
        self.set_content_height(800)

        # Schedule page
        schedule_page = Adw.PreferencesPage(title="Scheduling", icon_name="alarm-symbolic")
        self.schedule_group = Adw.PreferencesGroup(title="Routine")

        # Add schedule button
        add_schedule_button = Gtk.Button()
        add_schedule_button.add_css_class("flat")
        schedule_button_content = Adw.ButtonContent(icon_name="list-add-symbolic", label="Add Schedule")
        add_schedule_button.set_child(schedule_button_content)
        add_schedule_button.connect("clicked", self.create_new_routine)
        self.schedule_group.set_header_suffix(add_schedule_button)

        for routine_id in self.config["Routine"].keys():
            schedule_row = ScheduleRow(routine_id, self.delete_routine, self.config)
            self.schedule_group.add(schedule_row)

        schedule_page.add(self.schedule_group)
        self.add(schedule_page)

        # A
        general_page = Adw.PreferencesPage(title="General", icon_name="emblem-system-symbolic")
        self.add(general_page)

    def create_new_routine(self, _):
        routine_ids_unparsed = self.config["Routine"]
        routine_ids = set((int(key) for key in routine_ids_unparsed.keys()))

        routine_id = 0
        # Iterates +1 to include maximum, +1 to include room for extra
        for potential_routine_id in range(max(routine_ids) + 1 + 1):
            if potential_routine_id not in routine_ids:
                routine_id = potential_routine_id
                break

        self.config["Routine"][str(routine_id)] = "day 23:59"
        schedule_row = ScheduleRow(str(routine_id), self.delete_routine, self.config)
        self.schedule_group.add(schedule_row)

    def delete_routine(self, row_self: ScheduleRow):
        del self.config["Routine"][row_self.id]
        with open(CONFIG_PATH, "w") as w:
            self.config.write(w)

        self.schedule_group.remove(row_self)

    def display_save_dialog(self, _):
        save_dialog = Adw.AlertDialog(title="Save Changes?")
        save_dialog.add_response("save", "Save")
        save_dialog.set_title("AAA")
        save_dialog.set_body("Changes have been detected. Do you want to save and apply these?")
        save_dialog.add_response("cancel", "Cancel")
        save_dialog.present(self)
