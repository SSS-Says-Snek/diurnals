from configparser import ConfigParser

from gi.repository import Adw, Gtk

from src.constants import CONFIG_PATH, API_KEY_PATH
from src.config_schedule_row import ScheduleRow


class ConfigWindow(Adw.PreferencesDialog):
    def __init__(self, api_key: str, config: ConfigParser, banner: Adw.Banner, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.api_key = api_key
        self.config = config
        self.banner = banner
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

        self.schedule_rows: list[ScheduleRow] = []
        for routine_id in self.config["Routine"].keys():
            schedule_row = ScheduleRow(routine_id, self.delete_routine, self.config)
            self.schedule_rows.append(schedule_row)
            self.schedule_group.add(schedule_row)

        schedule_page.add(self.schedule_group)
        self.add(schedule_page)

        # GENERAL PAGE
        general_page = Adw.PreferencesPage(title="General", icon_name="emblem-system-symbolic")
        filter_group = Adw.PreferencesGroup(title="Filters")
        self.filter_entry = Adw.EntryRow(title="Enter your Todoist filter", text=self.config["General"]["filter"])
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

        if (new_text := self.filter_entry.get_text()) != self.config["General"]["filter"]:
            self.config["General"]["filter"] = new_text
            config_changed = True
        if (new_api_key := self.api_key_entry.get_text()) != self.get_file_api_key():
            API_KEY_PATH.write_text(f"API_KEY={new_api_key}")
            config_changed = True

        for schedule_row in self.schedule_rows:
            if schedule_row.check_if_updated():
                config_changed = True

        if config_changed:
            self.banner.set_revealed(True)
        with open(CONFIG_PATH, "w") as w:
            self.config.write(w)

    def create_new_routine(self, _):
        routine_ids_unparsed = self.config["Routine"]
        routine_ids = set((int(key) for key in routine_ids_unparsed.keys()))

        routine_id = 0
        # Iterates +1 to include maximum, +1 to include room for extra
        for potential_routine_id in range(max(routine_ids) + 1 + 1):
            if potential_routine_id not in routine_ids:
                routine_id = potential_routine_id
                break

        self.config["Routine"][str(routine_id)] = "day 23:59"  # Set default time
        schedule_row = ScheduleRow(str(routine_id), self.delete_routine, self.config)
        self.schedule_group.add(schedule_row)

    def delete_routine(self, row_self: ScheduleRow):
        del self.config["Routine"][row_self.id]
        with open(CONFIG_PATH, "w") as w:
            self.config.write(w)

        self.schedule_group.remove(row_self)

    @staticmethod
    def get_file_api_key():
        return API_KEY_PATH.read_text().replace("API_KEY=", "").strip()
