from collections.abc import Callable
from datetime import date, datetime, timedelta

from gi.repository import Gtk
from todoist_api_python.models import Task


class TodoistElement(Gtk.ListBoxRow):
    def __init__(
        self,
        task: Task,
        callback: Callable[[Gtk.CheckButton, "TodoistElement"], None],
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.task = task

        self.set_selectable(False)
        self.due_date = None

        hbox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=24,
            margin_start=12,
            margin_end=12,
            margin_top=6,
            margin_bottom=6,
        )
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, halign=Gtk.Align.FILL)
        self.check_button = Gtk.CheckButton()
        self.check_button.connect("toggled", lambda button: callback(button, self))

        label = Gtk.Label(label=task.content, halign=Gtk.Align.START)
        vbox.append(label)

        if self.task.due is not None:  # Set due date label
            label = "Due {}"
            css_classes = ["due-date"]
            due_date_str = self.task.due.date
            self.due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

            days_left = self.due_date - date.today()
            if days_left < timedelta(days=0):
                label = "Overdue"
                css_classes.append("overdue")
            elif days_left == timedelta(days=0):
                due_date_str = "today"
                css_classes.append("due-today")
            elif days_left < timedelta(days=7):  # If less than a week, you can just refer to it by the weekday
                due_date_str = self.due_date.strftime("%A")
            else:
                due_date_str = self.due_date.strftime("%b %-d")

            due_date_label = Gtk.Label(label=label.format(due_date_str), halign=Gtk.Align.START)  # Stupid noqa idk
            due_date_label.set_css_classes(css_classes)
            vbox.append(due_date_label)

        hbox.append(self.check_button)
        hbox.append(vbox)
        self.set_child(hbox)

    @staticmethod
    def sort_rows(left: "TodoistElement", right: "TodoistElement"):
        if left.due_date is None and right.due_date is None:  # If there's no due date for both, they're equal
            return 0
        elif left.due_date is not None and right.due_date is None:  # If L has due date, but R doesn't, L gets moved up
            return -1
        elif (
            left.due_date is None and right.due_date is not None
        ):  # If R has due date, but L doesn't, L gets moved down
            return 1
        elif left.due_date is not None and right.due_date is not None:  # for the type hint
            if left.due_date < right.due_date:
                return -1
            elif left.due_date == right.due_date:
                return 0
            elif left.due_date > right.due_date:
                return 1
