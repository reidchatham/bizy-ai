"""Live CLI Dashboard for Bizy AI

Real-time terminal UI showing:
- Today's tasks
- Active goals with progress
- Quick stats (velocity, completion rate)
- Upcoming deadlines
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, ProgressBar
from textual.reactive import reactive
from datetime import datetime, timedelta
from agent.tasks import TaskManager
from agent.planner import BusinessPlanner


class StatsWidget(Static):
    """Display key statistics"""

    def compose(self) -> ComposeResult:
        yield Static("", id="stats-content")

    def update_stats(self, task_mgr: TaskManager):
        """Update statistics display"""
        today_summary = task_mgr.get_daily_summary()
        velocity = task_mgr.get_task_velocity(days=7)
        weekly_stats = task_mgr.get_weekly_task_stats()

        stats_text = f"""[bold cyan]📊 Statistics[/bold cyan]

[bold]Today:[/bold]
  • Completed: {today_summary['tasks_completed']} tasks

[bold]This Week:[/bold]
  • Completed: {weekly_stats['tasks_completed_this_week']} tasks
  • Completion Rate: {weekly_stats['completion_rate']:.1f}%
  • Velocity: {velocity:.1f} tasks/day
"""
        self.query_one("#stats-content", Static).update(stats_text)


class TasksWidget(Static):
    """Display today's tasks"""

    def compose(self) -> ComposeResult:
        table = DataTable(id="tasks-table")
        table.add_columns("✓", "Priority", "Task", "Category")
        yield table

    def update_tasks(self, task_mgr: TaskManager):
        """Update tasks display"""
        table = self.query_one("#tasks-table", DataTable)
        table.clear()

        # Get today's tasks
        tasks = task_mgr.get_tasks_for_today()

        if not tasks:
            # Get next 10 pending tasks if no tasks for today
            from agent.models import Task
            tasks = task_mgr.session.query(Task).filter(
                Task.status.in_(['pending', 'in_progress'])
            ).limit(10).all()

        for task in tasks[:10]:  # Limit to 10 tasks
            status = "✓" if task.status == 'completed' else "○"
            priority = "🔴" if task.priority == 1 else "🟡" if task.priority == 2 else "🟢"
            title = task.title[:40] if len(task.title) > 40 else task.title
            category = task.category or "-"

            table.add_row(status, priority, title, category)


class GoalsWidget(Static):
    """Display active goals"""

    def compose(self) -> ComposeResult:
        yield Static("", id="goals-content")

    def update_goals(self, planner: BusinessPlanner):
        """Update goals display"""
        goals = planner.get_active_goals()

        if not goals:
            content = "[yellow]No active goals[/yellow]"
        else:
            content = "[bold cyan]🎯 Active Goals[/bold cyan]\n\n"
            for goal in goals[:5]:  # Show top 5 goals
                progress_bar = "█" * int(goal.progress_percentage / 10)
                progress_bar += "░" * (10 - int(goal.progress_percentage / 10))
                content += f"[bold]{goal.title[:40]}[/bold]\n"
                content += f"{progress_bar} {goal.progress_percentage:.0f}%\n\n"

        self.query_one("#goals-content", Static).update(content)


class BizyDashboard(App):
    """Bizy AI Live Dashboard"""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 2;
        grid-rows: 1fr 1fr;
        grid-columns: 1fr 1fr;
    }

    StatsWidget {
        border: solid $accent;
        height: 100%;
        padding: 1;
    }

    TasksWidget {
        border: solid $accent;
        height: 100%;
        padding: 1;
        column-span: 2;
    }

    GoalsWidget {
        border: solid $accent;
        height: 100%;
        padding: 1;
    }

    #tasks-table {
        height: 100%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the dashboard."""
        yield Header()
        yield StatsWidget()
        yield GoalsWidget()
        yield TasksWidget()
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts."""
        self.title = "Bizy AI Dashboard"
        self.sub_title = f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
        self.refresh_data()

        # Set up auto-refresh every 30 seconds
        self.set_interval(30, self.refresh_data)

    def refresh_data(self) -> None:
        """Refresh all data"""
        task_mgr = TaskManager()
        planner = BusinessPlanner()

        # Update all widgets
        self.query_one(StatsWidget).update_stats(task_mgr)
        self.query_one(TasksWidget).update_tasks(task_mgr)
        self.query_one(GoalsWidget).update_goals(planner)

        # Update subtitle with refresh time
        self.sub_title = f"Last updated: {datetime.now().strftime('%H:%M:%S')}"

        task_mgr.close()
        planner.close()

    def action_refresh(self) -> None:
        """Manual refresh action"""
        self.refresh_data()


def run_dashboard():
    """Run the dashboard"""
    app = BizyDashboard()
    app.run()


if __name__ == "__main__":
    run_dashboard()
