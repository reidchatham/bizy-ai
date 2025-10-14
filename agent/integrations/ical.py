"""iCalendar integration for Bizy AI

Provides functionality to:
- Export tasks as .ics files
- Read local .ics files
- Sync tasks with calendar applications (Apple Calendar, Google Calendar, etc.)
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from icalendar import Calendar, Event
from agent.models import Task


class ICalIntegration:
    """Handles iCalendar file operations for task synchronization"""

    def __init__(self, calendar_dir: Optional[Path] = None):
        """Initialize iCal integration

        Args:
            calendar_dir: Directory to store .ics files (default: ~/.business-agent/calendar/)
        """
        if calendar_dir is None:
            calendar_dir = Path.home() / ".business-agent" / "calendar"

        self.calendar_dir = Path(calendar_dir)
        self.calendar_dir.mkdir(parents=True, exist_ok=True)
        self.calendar_file = self.calendar_dir / "bizy_tasks.ics"

    def export_tasks(self, tasks: List[Task], calendar_name: str = "Bizy AI Tasks") -> Path:
        """Export tasks to an iCalendar file

        Args:
            tasks: List of Task objects to export
            calendar_name: Name of the calendar

        Returns:
            Path to the generated .ics file
        """
        cal = Calendar()
        cal.add('prodid', '-//Bizy AI//bizy-ai//EN')
        cal.add('version', '2.0')
        cal.add('x-wr-calname', calendar_name)
        cal.add('x-wr-caldesc', 'Tasks from Bizy AI')

        for task in tasks:
            event = Event()

            # Basic task info
            event.add('summary', task.title)
            event.add('uid', f'bizy-task-{task.id}@bizy-ai')

            # Add description if available
            if task.notes:
                event.add('description', task.notes)

            # Add category
            if task.category:
                event.add('categories', [task.category])

            # Set dates
            if task.due_date:
                # All-day event for tasks with due dates
                event.add('dtstart', task.due_date.date())
                event.add('dtend', (task.due_date + timedelta(days=1)).date())
            else:
                # Use created_at if no due date
                event.add('dtstart', task.created_at)
                event.add('dtend', task.created_at + timedelta(hours=1))

            # Set status based on task completion
            if task.status == 'completed':
                event.add('status', 'COMPLETED')
                if task.completed_at:
                    event.add('completed', task.completed_at)
            else:
                event.add('status', 'NEEDS-ACTION')

            # Set priority (1-9 scale, where 1 is highest)
            # Task priority: 1=High, 2=Medium, 3=Low
            # iCal priority: 1-4=High, 5=Medium, 6-9=Low
            if task.priority == 1:
                event.add('priority', 1)  # High
            elif task.priority == 2:
                event.add('priority', 5)  # Medium
            else:
                event.add('priority', 9)  # Low

            # Add created/modified timestamps
            event.add('created', task.created_at)
            if hasattr(task, 'updated_at') and task.updated_at:
                event.add('last-modified', task.updated_at)
            else:
                event.add('last-modified', task.created_at)

            cal.add_component(event)

        # Write to file
        with open(self.calendar_file, 'wb') as f:
            f.write(cal.to_ical())

        return self.calendar_file

    def import_calendar(self, ical_path: Optional[Path] = None) -> Calendar:
        """Import an iCalendar file

        Args:
            ical_path: Path to .ics file (default: uses calendar_file)

        Returns:
            Calendar object
        """
        if ical_path is None:
            ical_path = self.calendar_file

        if not Path(ical_path).exists():
            raise FileNotFoundError(f"Calendar file not found: {ical_path}")

        with open(ical_path, 'rb') as f:
            return Calendar.from_ical(f.read())

    def get_events(self, ical_path: Optional[Path] = None) -> List[dict]:
        """Get all events from an iCalendar file

        Args:
            ical_path: Path to .ics file

        Returns:
            List of event dictionaries
        """
        cal = self.import_calendar(ical_path)
        events = []

        for component in cal.walk():
            if component.name == "VEVENT":
                event = {
                    'summary': str(component.get('summary', '')),
                    'description': str(component.get('description', '')),
                    'start': component.get('dtstart').dt,
                    'end': component.get('dtend').dt if component.get('dtend') else None,
                    'status': str(component.get('status', 'NEEDS-ACTION')),
                    'priority': int(component.get('priority', 5)),
                    'uid': str(component.get('uid', '')),
                    'categories': [str(cat) for cat in component.get('categories', [])]
                }
                events.append(event)

        return events

    def get_export_path(self) -> Path:
        """Get the path where calendar files are stored

        Returns:
            Path to calendar directory
        """
        return self.calendar_file

    def create_single_task_event(self, task: Task, filename: Optional[str] = None) -> Path:
        """Export a single task as an .ics file for importing into calendar apps

        Args:
            task: Task to export
            filename: Optional custom filename (default: task-{id}.ics)

        Returns:
            Path to the generated .ics file
        """
        if filename is None:
            filename = f"task-{task.id}.ics"

        export_path = self.calendar_dir / filename

        # Create calendar with single event
        cal = Calendar()
        cal.add('prodid', '-//Bizy AI//bizy-ai//EN')
        cal.add('version', '2.0')

        event = Event()
        event.add('summary', task.title)
        event.add('uid', f'bizy-task-{task.id}@bizy-ai')

        if task.notes:
            event.add('description', task.notes)

        if task.category:
            event.add('categories', [task.category])

        # Set dates
        if task.due_date:
            event.add('dtstart', task.due_date.date())
            event.add('dtend', (task.due_date + timedelta(days=1)).date())
        else:
            event.add('dtstart', task.created_at)
            event.add('dtend', task.created_at + timedelta(hours=1))

        cal.add_component(event)

        # Write to file
        with open(export_path, 'wb') as f:
            f.write(cal.to_ical())

        return export_path
