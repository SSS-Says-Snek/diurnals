from gi.repository import Gtk, Adw

from datetime import datetime


class ScheduleRow(Adw.ActionRow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        box = Gtk.Box(spacing=6, margin_start=12, margin_end=12, margin_top=6, margin_bottom=6)
        box.add_css_class("card")
        box.append(Gtk.Label(label="Activate every"))

        self.day_option = Gtk.DropDown.new_from_strings(
            [
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
        )
        day_child = self.day_option.get_first_child()
        if day_child is not None:
            day_child.add_css_class("flat")  # There's no flat option for dropdowns :( so here's a workaround
        box.append(self.day_option)
        box.append(Gtk.Label(label="at"))

        # Box to hold hour, minute, and that goofy ahh colon
        time_box = Gtk.Box()
        self.hour_option = Gtk.SpinButton(
            css_classes=["flat"],
            orientation=Gtk.Orientation.VERTICAL,
            adjustment=Gtk.Adjustment(value=11, lower=1, upper=12, step_increment=1),
        )
        self.hour_option.connect("output", self.round_to_int)
        self.minute_option = Gtk.SpinButton(
            css_classes=["flat"],
            orientation=Gtk.Orientation.VERTICAL,
            adjustment=Gtk.Adjustment(value=59, lower=0, upper=59, step_increment=1),
        )
        self.minute_option.connect("output", self.round_to_int)

        box.append(self.hour_option)
        box.append(Gtk.Label(label=":"))
        box.append(self.minute_option)
        box.append(time_box)

        # AM/PM
        self.am_pm_option = Gtk.DropDown.new_from_strings(["PM", "AM"])
        am_pm_child = self.am_pm_option.get_first_child()
        if am_pm_child is not None:
            am_pm_child.add_css_class("flat")  # Always true, but here for the type hint
        box.append(self.am_pm_option)

        self.set_child(box)

    @staticmethod
    def round_to_int(spin_button: Gtk.SpinButton):
        adjustment = spin_button.get_adjustment()
        spin_button.set_text(f"{int(adjustment.get_value()):02d}")
        return True

    def get_options(self, _):
        result = {}
        day_item = self.day_option.get_selected_item()
        am_pm_item = self.am_pm_option.get_selected_item()

        hour = self.hour_option.get_value_as_int()
        minute = self.minute_option.get_value_as_int()
        if isinstance(day_item, Gtk.StringObject):  # Always true, for the type hint
            result["day"] = day_item.get_string()
        if isinstance(am_pm_item, Gtk.StringObject):
            am_pm = am_pm_item.get_string()
            input_time = datetime.strptime(f"{hour}:{minute} {am_pm}", "%I:%M %p")
            result["time"] = datetime.strftime(input_time, f"%H:%M")
        print(result)


class ConfigWindow(Adw.PreferencesDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_content_width(1000)
        self.set_content_width(800)

        # Schedule page
        schedule_page = Adw.PreferencesPage(title="Scheduling", icon_name="alarm-symbolic")

        schedule_group = Adw.PreferencesGroup(title="Routine")

        # Add schedule button
        add_schedule_button = Gtk.Button()
        add_schedule_button.add_css_class("flat")
        schedule_button_content = Adw.ButtonContent(icon_name="list-add-symbolic", label="Add Schedule")
        add_schedule_button.set_child(schedule_button_content)

        schedule_group.set_header_suffix(add_schedule_button)
        schedule_group.add(Adw.SwitchRow(title="AAAA"))
        e = ScheduleRow()
        schedule_group.add(e)

        schedule_page.add(schedule_group)
        self.add(schedule_page)

        # A
        self.add(Adw.PreferencesPage(title="Ab"))

        self.connect("closed", e.get_options)
