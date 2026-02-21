from gi.repository import Adw, Gtk, GLib

from src.constants import API_KEY_PATH
from src.config_schedule_row import ScheduleRow

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.window import TodoistWindow

class ConfigWindow(Adw.PreferencesDialog):
    def __init__(self, parent: "TodoistWindow", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.api_key = parent.api_key
        self.banner = parent.banner
        self.settings = parent.settings
        self.connect("closed", self.save_preferences)

        # SCHEDULE PAGE
        schedule_page = Adw.PreferencesPage(title="Scheduling", icon_name="alarm-symbolic")
        self.schedule_group = Adw.PreferencesGroup(title="Routine")

        # Add schedule button
        add_schedule_button = Gtk.Button()
        add_schedule_button.add_css_class("flat")
        schedule_button_content = Adw.ButtonContent(icon_name="list-add-symbolic", label="Add Schedule")
        add_schedule_button.set_child(schedule_button_content)
        add_schedule_button.connect("clicked", self.create_new_routine)
        self.schedule_group.set_header_suffix(add_schedule_button)

        self.routines = self.settings.get_value("routines").unpack()
        self.schedule_rows: list[ScheduleRow] = []
        for routine in self.routines:
            schedule_row = ScheduleRow(routine, self.delete_routine)
            self.schedule_rows.append(schedule_row)
            self.schedule_group.add(schedule_row)
        self.old_schedule_rows = self.schedule_rows.copy()

        schedule_page.add(self.schedule_group)
        self.add(schedule_page)

        # GENERAL PAGE
        general_page = Adw.PreferencesPage(title="General", icon_name="emblem-system-symbolic")
        filter_group = Adw.PreferencesGroup(title="Filters")
        self.filter_entry = Adw.EntryRow(title="Enter your Todoist filter", text=self.settings.get_string("tasks-filter"))
        filter_group.add(self.filter_entry)

        general_group = Adw.PreferencesGroup(title="General")
        self.api_key_entry = Adw.PasswordEntryRow(title="Enter your Todoist API Key", text=self.api_key)
        general_group.add(self.api_key_entry)

        general_page.add(filter_group)
        general_page.add(general_group)
        self.add(general_page)

    def save_preferences(self, _):
        """Checks if config changed; if did, reveal banner and save to files"""
        config_changed = False

        if (new_text := self.filter_entry.get_text()) != self.settings.get_string("tasks-filter"):
            self.settings.set_string("tasks-filter", new_text)
            config_changed = True
        if (new_api_key := self.api_key_entry.get_text()) != self.get_file_api_key():
            API_KEY_PATH.write_text(f"API_KEY={new_api_key}")
            config_changed = True

        for schedule_row in self.schedule_rows:
            if schedule_row.check_if_updated():
                idx = self.routines.index(schedule_row.old_values)
                self.routines[idx] = schedule_row.get_options()
                config_changed = True
        if len(self.old_schedule_rows) != len(self.schedule_rows):
            config_changed = True

        if config_changed:
            self.settings.set_value("routines", GLib.Variant("as", self.routines))
            self.banner.set_revealed(True)

    def create_new_routine(self, _):
        self.routines.append("day 23:59")

        schedule_row = ScheduleRow("day 23:59", self.delete_routine)
        self.schedule_rows.append(schedule_row)
        self.schedule_group.add(schedule_row)

    def delete_routine(self, row_self: ScheduleRow):
        self.routines.remove(row_self.old_values)
        self.schedule_rows.remove(row_self)
        self.schedule_group.remove(row_self)

    @staticmethod
    def get_file_api_key():
        return API_KEY_PATH.read_text().replace("API_KEY=", "").strip()
