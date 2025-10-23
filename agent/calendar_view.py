"""Native CLI Calendar View with Textual

Interactive calendar showing tasks by date:
- Month view with task counts per day
- Week view with task details
- Navigation between months/weeks
- Task filtering and selection
"""

from datetime import datetime, timedelta
from calendar import monthrange, day_name
from typing import List, Optional
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from agent.tasks import TaskManager
from agent.models import Task


class CalendarGrid(Static):
    """Calendar grid showing month view with task indicators"""

    current_month = reactive(datetime.now().month)
    current_year = reactive(datetime.now().year)
    selected_date = reactive(datetime.now().date())

    def __init__(self, task_mgr: TaskManager, **kwargs):
        super().__init__(**kwargs)
        self.task_mgr = task_mgr

    def compose(self) -> ComposeResult:
        """Create the calendar grid"""
        yield Static(id="calendar-grid")

    def watch_current_month(self, month: int) -> None:
        """React to month changes"""
        self.update_calendar()

    def watch_current_year(self, year: int) -> None:
        """React to year changes"""
        self.update_calendar()

    def watch_selected_date(self, date: datetime.date) -> None:
        """React to selected date changes"""
        self.update_calendar()
        # Notify parent app to update task list
        self.post_message(self.DateSelected(date))

    def on_mount(self) -> None:
        """Initialize calendar on mount"""
        self.update_calendar()

    class DateSelected(Message):
        """Message sent when a date is selected"""
        def __init__(self, date: datetime.date) -> None:
            self.date = date
            super().__init__()

    def update_calendar(self) -> None:
        """Render the calendar grid"""
        # Get calendar data
        month_name = datetime(self.current_year, self.current_month, 1).strftime('%B %Y')
        first_day = datetime(self.current_year, self.current_month, 1)
        days_in_month = monthrange(self.current_year, self.current_month)[1]
        start_weekday = first_day.weekday()  # 0 = Monday

        # Get tasks for this month
        month_start = datetime(self.current_year, self.current_month, 1)
        month_end = datetime(self.current_year, self.current_month, days_in_month, 23, 59, 59)

        tasks = self.task_mgr.session.query(Task).filter(
            Task.due_date >= month_start,
            Task.due_date <= month_end
        ).all()

        # Count tasks per day
        task_counts = {}
        for task in tasks:
            if task.due_date:
                day = task.due_date.day
                task_counts[day] = task_counts.get(day, 0) + 1

        # Build calendar display
        lines = []
        lines.append(f"[bold cyan]{month_name}[/bold cyan]")
        lines.append("")

        # Day headers
        headers = "  Mo  Tu  We  Th  Fr  Sa  Su"
        lines.append(f"[bold]{headers}[/bold]")

        # Calendar grid
        current_day = 1
        week = []

        # Add empty cells for days before month starts
        for _ in range(start_weekday):
            week.append("    ")

        # Add days of month
        while current_day <= days_in_month:
            date = datetime(self.current_year, self.current_month, current_day).date()
            count = task_counts.get(current_day, 0)

            # Highlight today and selected date
            if date == datetime.now().date():
                day_str = f"[bold green]{current_day:2d}[/bold green]"
            elif date == self.selected_date:
                day_str = f"[bold yellow]{current_day:2d}[/bold yellow]"
            else:
                day_str = f"{current_day:2d}"

            # Add task count indicator
            if count > 0:
                day_str = f"{day_str}•"
            else:
                day_str = f"{day_str} "

            week.append(f" {day_str} ")

            # New week
            if len(week) == 7:
                lines.append("".join(week))
                week = []

            current_day += 1

        # Add remaining days
        if week:
            while len(week) < 7:
                week.append("    ")
            lines.append("".join(week))

        # Add legend
        lines.append("")
        lines.append("[dim]• = has tasks  [green]●[/green] = today  [yellow]●[/yellow] = selected[/dim]")
        lines.append("[dim]← → = prev/next day  ↑ ↓ = prev/next week  Ctrl+← → = prev/next month[/dim]")
        lines.append("[dim]T = today  R = refresh  Q = quit[/dim]")

        # Update display
        grid = self.query_one("#calendar-grid", Static)
        grid.update("\n".join(lines))

    def next_month(self) -> None:
        """Navigate to next month"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1

    def prev_month(self) -> None:
        """Navigate to previous month"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1

    def select_day(self, day: int) -> None:
        """Select a specific day"""
        self.selected_date = datetime(self.current_year, self.current_month, day).date()

    def next_day(self) -> None:
        """Navigate to next day"""
        new_date = self.selected_date + timedelta(days=1)
        if new_date.month != self.current_month:
            self.current_month = new_date.month
            self.current_year = new_date.year
        self.selected_date = new_date

    def prev_day(self) -> None:
        """Navigate to previous day"""
        new_date = self.selected_date - timedelta(days=1)
        if new_date.month != self.current_month:
            self.current_month = new_date.month
            self.current_year = new_date.year
        self.selected_date = new_date


class TaskListWidget(Static):
    """Show tasks for selected date"""

    def __init__(self, task_mgr: TaskManager, **kwargs):
        super().__init__(**kwargs)
        self.task_mgr = task_mgr
        self.current_date = datetime.now().date()

    def compose(self) -> ComposeResult:
        """Create task list display"""
        yield Static(id="task-list")

    def on_mount(self) -> None:
        """Initialize task list"""
        self.update_tasks()

    def update_tasks(self, date: Optional[datetime.date] = None) -> None:
        """Update task list for given date"""
        if date:
            self.current_date = date

        # Get tasks for this date
        day_start = datetime.combine(self.current_date, datetime.min.time())
        day_end = datetime.combine(self.current_date, datetime.max.time())

        tasks = self.task_mgr.session.query(Task).filter(
            Task.due_date >= day_start,
            Task.due_date <= day_end
        ).order_by(Task.priority.asc(), Task.created_at.asc()).all()

        # Build task list display
        lines = []
        lines.append(f"[bold cyan]Tasks for {self.current_date.strftime('%A, %B %d, %Y')}[/bold cyan]")
        lines.append("")

        if not tasks:
            lines.append("[dim]No tasks scheduled for this day[/dim]")
        else:
            for task in tasks:
                # Status indicator
                if task.status == 'completed':
                    status = "[green]✓[/green]"
                elif task.status == 'in_progress':
                    status = "[yellow]◐[/yellow]"
                else:
                    status = "[dim]○[/dim]"

                # Priority indicator
                if task.priority == 1:
                    priority = "[red]●[/red]"
                elif task.priority == 2:
                    priority = "[yellow]●[/yellow]"
                else:
                    priority = "[dim]●[/dim]"

                # Task info
                title = task.title[:50] + "..." if len(task.title) > 50 else task.title
                time_str = task.due_date.strftime('%H:%M') if task.due_date else ""

                lines.append(f"{status} {priority} [{time_str}] {title}")

        # Update display
        task_list = self.query_one("#task-list", Static)
        task_list.update("\n".join(lines))


class CalendarApp(App):
    """Bizy AI Calendar View - Interactive task calendar"""

    CSS = """
    Screen {
        background: $surface;
    }

    #calendar-container {
        height: 100%;
        padding: 1;
    }

    #calendar-grid {
        height: 1fr;
        padding: 1;
        border: solid $primary;
        background: $panel;
    }

    #task-list {
        height: 1fr;
        padding: 1;
        border: solid $primary;
        background: $panel;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("left", "prev_day", "Previous Day"),
        ("right", "next_day", "Next Day"),
        ("up", "prev_week", "Previous Week"),
        ("down", "next_week", "Next Week"),
        ("ctrl+left", "prev_month", "Previous Month"),
        ("ctrl+right", "next_month", "Next Month"),
        ("t", "today", "Today"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self):
        super().__init__()
        self.task_mgr = TaskManager()
        self.calendar = None
        self.task_list = None

    def compose(self) -> ComposeResult:
        """Create the calendar view layout"""
        yield Header()
        with Container(id="calendar-container"):
            self.calendar = CalendarGrid(self.task_mgr)
            self.task_list = TaskListWidget(self.task_mgr)
            yield self.calendar
            yield self.task_list
        yield Footer()

    def action_prev_day(self) -> None:
        """Navigate to previous day"""
        self.calendar.prev_day()

    def action_next_day(self) -> None:
        """Navigate to next day"""
        self.calendar.next_day()

    def action_prev_month(self) -> None:
        """Navigate to previous month"""
        self.calendar.prev_month()

    def action_next_month(self) -> None:
        """Navigate to next month"""
        self.calendar.next_month()

    def action_prev_week(self) -> None:
        """Select previous week"""
        new_date = self.calendar.selected_date - timedelta(days=7)
        if new_date.month != self.calendar.current_month:
            self.calendar.current_month = new_date.month
            self.calendar.current_year = new_date.year
        self.calendar.selected_date = new_date

    def action_next_week(self) -> None:
        """Select next week"""
        new_date = self.calendar.selected_date + timedelta(days=7)
        if new_date.month != self.calendar.current_month:
            self.calendar.current_month = new_date.month
            self.calendar.current_year = new_date.year
        self.calendar.selected_date = new_date

    def action_today(self) -> None:
        """Jump to today"""
        today = datetime.now()
        self.calendar.current_month = today.month
        self.calendar.current_year = today.year
        self.calendar.selected_date = today.date()

    def action_refresh(self) -> None:
        """Refresh the view"""
        self.calendar.update_calendar()
        self.task_list.update_tasks()

    def on_calendar_grid_date_selected(self, message: CalendarGrid.DateSelected) -> None:
        """Handle date selection from calendar"""
        self.task_list.update_tasks(message.date)

    def on_mount(self) -> None:
        """Initialize view on mount"""
        self.title = "Bizy AI Calendar"
        self.sub_title = "Navigate: ← → days  ↑ ↓ weeks  Ctrl+← → months  T=today  Q=quit"


def run_calendar():
    """Launch the calendar view"""
    app = CalendarApp()
    app.run()


if __name__ == "__main__":
    run_calendar()
