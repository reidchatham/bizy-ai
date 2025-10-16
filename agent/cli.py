#!/usr/bin/env python3
"""Business Agent CLI Tool"""

import click
import os
import sys
from agent.tasks import TaskManager
from agent.planner import BusinessPlanner
from agent.research import ResearchAgent
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
console = Console()

@click.group()
def cli():
    """Business Agent CLI - Manage your business from the command line"""
    pass

# TASK COMMANDS
@cli.group()
def task():
    """Manage tasks"""
    pass

@task.command()
@click.argument('title')
@click.option('--description', '-d', help='Task description')
@click.option('--priority', '-p', type=int, default=3)
@click.option('--category', '-c', help='Task category')
@click.option('--hours', '-h', type=float, help='Estimated hours')
@click.option('--goal', '-g', type=int, help='Goal ID to assign task to')
def add(title, description, priority, category, hours, goal):
    """Add a new task"""
    task_mgr = TaskManager()
    planner = BusinessPlanner()

    goal_id = goal

    # If no goal specified, prompt user to select or create one
    if goal_id is None:
        goals = planner.get_active_goals()

        if goals:
            console.print("\n[bold]📋 Available Goals:[/bold]")
            goals_table = Table(show_header=True, header_style="bold cyan")
            goals_table.add_column("ID", style="dim", width=6)
            goals_table.add_column("Goal")
            goals_table.add_column("Progress", justify="right", width=15)

            for g in goals[:10]:  # Show max 10 goals
                progress_bar = "█" * int(g.progress_percentage / 10) + "░" * (10 - int(g.progress_percentage / 10))
                goals_table.add_row(
                    str(g.id),
                    g.title[:50],
                    f"{progress_bar} {g.progress_percentage:.0f}%"
                )
            console.print(goals_table)

            # Prompt user
            console.print("\n[bold]Options:[/bold]")
            console.print("  • Enter [cyan]goal ID[/cyan] to assign task to that goal")
            console.print("  • Press [dim]Enter[/dim] to skip (create task without goal)")
            console.print("  • Type [yellow]'new'[/yellow] to create a new goal")

            choice = Prompt.ask("\n[bold]Your choice[/bold]", default="")

            if choice.lower() == 'new':
                # Create new goal interactively
                console.print("\n[bold cyan]Creating New Goal[/bold cyan]")
                goal_title = Prompt.ask("Goal title")
                goal_horizon = Prompt.ask(
                    "Horizon",
                    choices=["daily", "weekly", "monthly", "quarterly", "yearly"],
                    default="monthly"
                )

                try:
                    new_goal = planner.create_goal(
                        title=goal_title,
                        horizon=goal_horizon
                    )
                    goal_id = new_goal.id
                    console.print(f"[green]✓[/green] Created goal: {new_goal.title} (ID: {new_goal.id})\n")
                except Exception as e:
                    console.print(f"[red]✗[/red] Error creating goal: {e}")
                    console.print("[yellow]Creating task without goal assignment[/yellow]\n")
                    goal_id = None
            elif choice and choice.isdigit():
                goal_id = int(choice)
                # Validate goal exists
                goal_obj = planner.get_goal(goal_id)
                if not goal_obj:
                    console.print(f"[yellow]⚠[/yellow]  Goal #{goal_id} not found. Creating task without goal.\n")
                    goal_id = None
        else:
            console.print("\n[yellow]No active goals found.[/yellow]")
            if Confirm.ask("Would you like to create a new goal?", default=False):
                console.print("\n[bold cyan]Creating New Goal[/bold cyan]")
                goal_title = Prompt.ask("Goal title")
                goal_horizon = Prompt.ask(
                    "Horizon",
                    choices=["daily", "weekly", "monthly", "quarterly", "yearly"],
                    default="monthly"
                )

                try:
                    new_goal = planner.create_goal(
                        title=goal_title,
                        horizon=goal_horizon
                    )
                    goal_id = new_goal.id
                    console.print(f"[green]✓[/green] Created goal: {new_goal.title} (ID: {new_goal.id})\n")
                except Exception as e:
                    console.print(f"[red]✗[/red] Error creating goal: {e}\n")
                    goal_id = None

    # Create task with goal assignment
    task = task_mgr.create_task(
        title=title,
        description=description,
        priority=priority,
        category=category,
        estimated_hours=hours,
        parent_goal_id=goal_id
    )

    console.print(f"[green]✓[/green] Task created: {task.title} (ID: {task.id})")
    if goal_id:
        console.print(f"[dim]  Assigned to goal #{goal_id}[/dim]")
        # Recalculate goal progress
        planner.calculate_goal_progress(goal_id)

    task_mgr.close()
    planner.close()

@task.command()
@click.option('--filter', '-f', type=click.Choice(['all', 'pending', 'completed', 'today']), default='all', help='Filter tasks')
@click.option('--goal', '-g', type=int, help='Filter by goal ID')
def list(filter, goal):
    """List tasks with optional filters"""
    task_mgr = TaskManager()

    # Get tasks based on filter
    if filter == 'all':
        from agent.models import Task
        if goal:
            tasks = task_mgr.session.query(Task).filter_by(parent_goal_id=goal).all()
        else:
            tasks = task_mgr.session.query(Task).all()
    elif filter == 'completed':
        from agent.models import Task
        query = task_mgr.session.query(Task).filter_by(status='completed')
        if goal:
            query = query.filter_by(parent_goal_id=goal)
        tasks = query.all()
    elif filter == 'pending':
        from agent.models import Task
        query = task_mgr.session.query(Task).filter(Task.status.in_(['pending', 'in_progress']))
        if goal:
            query = query.filter_by(parent_goal_id=goal)
        tasks = query.all()
    else:  # today
        tasks = task_mgr.get_tasks_for_today()

    if not tasks:
        console.print(f"[yellow]No {filter} tasks found[/yellow]")
        task_mgr.close()
        return

    # Build title
    title_parts = ["📋 Your Tasks"]
    if filter != 'all':
        title_parts.append(f"({filter.title()})")
    if goal:
        title_parts.append(f"for Goal #{goal}")

    table = Table(title=" ".join(title_parts), show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Priority", justify="center")
    table.add_column("Title")
    table.add_column("Category", style="cyan")
    table.add_column("Due Date", style="dim")

    for task in tasks:
        status_icon = "✓" if task.status == 'completed' else "○"
        priority_str = "🔴" if task.priority == 1 else "🟡" if task.priority == 2 else "🟢"
        due_date = task.due_date.strftime('%Y-%m-%d') if task.due_date else "-"

        table.add_row(
            str(task.id),
            status_icon,
            priority_str,
            task.title[:50],
            task.category or "-",
            due_date
        )

    console.print(table)
    task_mgr.close()

@task.command()
@click.argument('task_id', type=int)
def complete(task_id):
    """Mark a task as complete"""
    task_mgr = TaskManager()
    task = task_mgr.complete_task(task_id)
    if task:
        console.print(f"[green]✓[/green] Completed: {task.title}")

        # Update goal progress if task is associated with a goal
        if task.parent_goal_id:
            from agent.planner import BusinessPlanner
            planner = BusinessPlanner()
            progress = planner.calculate_goal_progress(task.parent_goal_id)
            console.print(f"[dim]Goal progress updated: {progress:.1f}%[/dim]")
            planner.close()
    else:
        console.print(f"[red]✗[/red] Task {task_id} not found")
    task_mgr.close()

# GOAL COMMANDS
@cli.group()
def goal():
    """Manage goals"""
    pass

@goal.command()
@click.argument('title')
@click.option('--description', '-d', help='Goal description')
@click.option('--horizon', '-h', type=click.Choice(['weekly', 'monthly', 'quarterly', 'yearly']), default='monthly')
@click.option('--target', '-t', help='Target date (YYYY-MM-DD)')
def add(title, description, horizon, target):
    """Add a new goal"""
    planner = BusinessPlanner()
    target_date = None
    if target:
        target_date = datetime.strptime(target, '%Y-%m-%d')

    goal = planner.create_goal(
        title=title,
        description=description,
        horizon=horizon,
        target_date=target_date
    )
    console.print(f"[green]✓[/green] Goal created: {goal.title} (ID: {goal.id})")
    planner.close()

@goal.command()
def list():
    """List all active goals"""
    planner = BusinessPlanner()
    goals = planner.get_active_goals()

    if not goals:
        console.print("[yellow]No active goals[/yellow]")
        planner.close()
        return

    # Recalculate progress for all goals
    for goal in goals:
        planner.calculate_goal_progress(goal.id)

    # Refresh goals after recalculation
    goals = planner.get_active_goals()

    table = Table(title="🎯 Your Goals", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim")
    table.add_column("Title")
    table.add_column("Horizon", style="cyan")
    table.add_column("Progress", justify="right")

    for goal in goals:
        progress_bar = "█" * int(goal.progress_percentage / 10) + "░" * (10 - int(goal.progress_percentage / 10))
        table.add_row(
            str(goal.id),
            goal.title[:40],
            goal.horizon,
            f"{progress_bar} {goal.progress_percentage:.0f}%"
        )

    console.print(table)
    planner.close()

@goal.command()
@click.argument('goal_id', type=int)
def breakdown(goal_id):
    """Break down a goal into tasks using AI"""
    planner = BusinessPlanner()
    console.print(f"[cyan]Breaking down goal {goal_id}...[/cyan]")
    tasks = planner.break_down_goal(goal_id)

    if tasks:
        console.print(f"[green]✓[/green] Created {len(tasks)} tasks")
        for task in tasks:
            console.print(f"  • {task.title}")
    else:
        console.print("[red]✗[/red] Failed to break down goal")
    planner.close()

# RESEARCH COMMANDS
@cli.group()
def research():
    """Conduct research"""
    pass

@research.command()
@click.argument('topic')
@click.option('--goal', '-g', help='Business goal')
def topic(topic, goal):
    """Research a topic"""
    researcher = ResearchAgent()
    console.print(f"[cyan]Researching: {topic}...[/cyan]\n")

    result = researcher.research_topic(
        topic=topic,
        business_goal=goal or "General research",
        depth="standard"
    )

    if 'error' in result:
        console.print(f"[red]✗ Error:[/red] {result['error']}")
    else:
        console.print(Panel(
            Markdown(result['findings']),
            title=f"🔍 Research: {topic}",
            border_style="blue"
        ))
        console.print(f"\n[dim]Saved as research ID: {result['research_id']}[/dim]")
    researcher.close()

@research.command()
@click.argument('domain')
@click.argument('offering')
def competitors(domain, offering):
    """Research competitors"""
    researcher = ResearchAgent()
    console.print(f"[cyan]Analyzing competitive landscape...[/cyan]\n")

    result = researcher.research_competitors(domain, offering)

    if 'error' in result:
        console.print(f"[red]✗ Error:[/red] {result['error']}")
    else:
        console.print(Panel(
            Markdown(result['findings']),
            title="🏆 Competitive Analysis",
            border_style="blue"
        ))
    researcher.close()

# STATS COMMAND
@cli.command()
def stats():
    """Show statistics"""
    task_mgr = TaskManager()
    weekly_stats = task_mgr.get_weekly_task_stats()
    today_summary = task_mgr.get_daily_summary()
    yesterday_summary = task_mgr.get_yesterday_summary()
    velocity = task_mgr.get_task_velocity(days=7)  # Use 7-day velocity to match weekly context
    today_tasks = task_mgr.get_tasks_for_today()

    console.print("\n[bold cyan]📊 Your Statistics[/bold cyan]\n")

    # Today's stats
    console.print("[bold]Today:[/bold]")
    console.print(f"  • Tasks Completed: {today_summary['tasks_completed']}")
    console.print(f"  • Tasks Scheduled: {len(today_tasks)}")

    # Yesterday's stats
    console.print(f"\n[bold]Yesterday:[/bold]")
    console.print(f"  • Tasks Completed: {yesterday_summary['tasks_completed']}")

    # Weekly stats
    console.print(f"\n[bold]This Week:[/bold]")
    console.print(f"  • Tasks Completed: {weekly_stats['tasks_completed_this_week']}")
    console.print(f"  • Tasks Created: {weekly_stats['tasks_created_this_week']}")
    console.print(f"  • Completion Rate: {weekly_stats['completion_rate']:.1f}%")
    console.print(f"  • Total Hours (Estimated): {weekly_stats['total_estimated_hours']:.1f}h")
    if weekly_stats['total_actual_hours'] > 0:
        console.print(f"  • Total Hours (Actual): {weekly_stats['total_actual_hours']:.1f}h")

    console.print(f"\n[bold]Velocity:[/bold] {velocity:.1f} tasks/day\n")

    # Show breakdown by category if available
    if weekly_stats['categories']:
        console.print("[bold]By Category (This Week):[/bold]")
        for category, count in sorted(weekly_stats['categories'].items(), key=lambda x: x[1], reverse=True):
            console.print(f"  • {category}: {count} task(s)")
        console.print()

    task_mgr.close()

# ANALYTICS/PREDICTIONS
@cli.group()
def predict():
    """Predictive analytics and forecasts"""
    pass

@predict.command()
@click.argument('goal_id', type=int)
@click.option('--velocity-days', '-v', type=int, default=30, help='Days to calculate velocity over')
def goal(goal_id, velocity_days):
    """Predict when a goal will be completed"""
    from agent.analytics import VelocityPredictor

    predictor = VelocityPredictor()
    prediction = predictor.predict_goal_completion(goal_id, velocity_days)

    if 'error' in prediction:
        console.print(f"[red]✗[/red] {prediction['error']}")
        predictor.close()
        return

    console.print(f"\n[bold cyan]🔮 Prediction for: {prediction['goal_title']}[/bold cyan]\n")

    if prediction['status'] == 'complete':
        console.print("[green]✓[/green] All tasks completed!")
    elif prediction['status'] == 'no_velocity':
        console.print(f"[yellow]{prediction['message']}[/yellow]")
        console.print(f"[dim]Remaining tasks: {prediction['remaining_tasks']}[/dim]")
    else:
        console.print(f"[bold]Remaining Tasks:[/bold] {prediction['remaining_tasks']}")
        console.print(f"[bold]Current Velocity:[/bold] {prediction['current_velocity']:.2f} tasks/day")
        console.print(f"[bold]Days Needed:[/bold] {prediction['days_needed']:.1f} days")
        console.print(f"[bold]Predicted Completion:[/bold] {prediction['predicted_completion'].strftime('%Y-%m-%d')}")

        if prediction['target_date']:
            console.print(f"[bold]Target Date:[/bold] {prediction['target_date'].strftime('%Y-%m-%d')}")

            if prediction['on_track']:
                console.print(f"\n[green]✓ On track to meet target date![/green]")
            else:
                console.print(f"\n[red]{prediction['warning']}[/red]")
                console.print(f"[dim]Consider extending deadline or reducing scope[/dim]")

    console.print()
    predictor.close()

@predict.command()
def all():
    """Show predictions for all active goals"""
    from agent.analytics import VelocityPredictor

    predictor = VelocityPredictor()
    predictions = predictor.get_all_goal_predictions()

    if not predictions:
        console.print("[yellow]No active goals found[/yellow]")
        predictor.close()
        return

    console.print("\n[bold cyan]🔮 Goal Completion Predictions[/bold cyan]\n")

    for pred in predictions:
        if 'error' in pred:
            continue

        status_icon = "✓" if pred['status'] == 'complete' else "⚠️" if not pred.get('on_track', True) else "✓"

        console.print(f"{status_icon} [bold]{pred['goal_title']}[/bold]")

        if pred['status'] == 'complete':
            console.print(f"  [green]All tasks completed![/green]\n")
        elif pred['status'] == 'no_velocity':
            console.print(f"  [yellow]{pred['message']}[/yellow]")
            console.print(f"  Remaining: {pred['remaining_tasks']} tasks\n")
        else:
            console.print(f"  Remaining: {pred['remaining_tasks']} tasks")
            console.print(f"  Velocity: {pred['current_velocity']:.2f} tasks/day")
            console.print(f"  Predicted: {pred['predicted_completion'].strftime('%Y-%m-%d')}")

            if pred.get('warning'):
                console.print(f"  [red]{pred['warning']}[/red]")
            console.print()

    predictor.close()

@predict.command()
@click.argument('goal_id', type=int)
def required(goal_id):
    """Calculate required velocity to complete goal on time"""
    from agent.analytics import VelocityPredictor

    predictor = VelocityPredictor()
    result = predictor.calculate_required_velocity(goal_id)

    if 'error' in result:
        console.print(f"[red]✗[/red] {result['error']}")
        predictor.close()
        return

    console.print(f"\n[bold cyan]Required Velocity for: {result['goal_title']}[/bold cyan]\n")

    if result['status'] == 'complete':
        console.print("[green]✓[/green] All tasks completed!")
    elif result['status'] == 'overdue':
        console.print(f"[red]Target date has passed[/red]")
        console.print(f"[dim]Remaining tasks: {result['remaining_tasks']}[/dim]")
    else:
        console.print(f"[bold]Remaining Tasks:[/bold] {result['remaining_tasks']}")
        console.print(f"[bold]Days Until Target:[/bold] {result['days_until_target']} days")
        console.print(f"[bold]Required Velocity:[/bold] {result['required_velocity']:.2f} tasks/day")
        console.print(f"[bold]Current Velocity:[/bold] {result['current_velocity']:.2f} tasks/day")
        console.print(f"[bold]Velocity Gap:[/bold] {result['velocity_gap']:.2f} tasks/day")

        if result['feasible']:
            console.print(f"\n[green]✓ Target is achievable with moderate effort increase[/green]")
        else:
            console.print(f"\n[red]⚠️  Significant velocity increase required[/red]")
            console.print(f"[dim]Consider extending deadline or reducing scope[/dim]")

    console.print()
    predictor.close()

# CHART COMMANDS
@cli.group()
def chart():
    """Generate terminal charts and visualizations"""
    pass

@chart.command()
@click.option('--days', '-d', type=int, default=30, help='Number of days to analyze')
def velocity(days):
    """Show velocity trend chart"""
    from agent.charts import ChartGenerator

    chart_gen = ChartGenerator()
    chart_output = chart_gen.velocity_chart(days=days)
    console.print(chart_output)
    chart_gen.close()

@chart.command()
def goals():
    """Show goal progress chart"""
    from agent.charts import ChartGenerator

    chart_gen = ChartGenerator()
    chart_output = chart_gen.goal_progress_chart()
    console.print(chart_output)
    chart_gen.close()

@chart.command()
@click.option('--days', '-d', type=int, default=30, help='Number of days to analyze')
def categories(days):
    """Show task distribution by category"""
    from agent.charts import ChartGenerator

    chart_gen = ChartGenerator()
    chart_output = chart_gen.category_distribution(days=days)
    console.print(chart_output)
    chart_gen.close()

@chart.command()
@click.argument('goal_id', type=int)
def burndown(goal_id):
    """Show burndown chart for a goal"""
    from agent.charts import ChartGenerator

    chart_gen = ChartGenerator()
    chart_output = chart_gen.burndown_chart(goal_id)
    console.print(chart_output)
    chart_gen.close()

@chart.command()
@click.option('--days', '-d', type=int, default=30, help='Number of days to analyze')
def productivity(days):
    """Show productivity heatmap by day of week"""
    from agent.charts import ChartGenerator

    chart_gen = ChartGenerator()
    chart_output = chart_gen.productivity_heatmap(days=days)
    console.print(chart_output)
    chart_gen.close()

@chart.command()
@click.option('--days', '-d', type=int, default=30, help='Number of days to analyze')
def priorities(days):
    """Show task breakdown by priority"""
    from agent.charts import ChartGenerator

    chart_gen = ChartGenerator()
    chart_output = chart_gen.priority_breakdown(days=days)
    console.print(chart_output)
    chart_gen.close()

@chart.command()
@click.option('--days', '-d', type=int, default=7, help='Number of days per period')
def comparison(days):
    """Compare current vs previous period"""
    from agent.charts import ChartGenerator

    chart_gen = ChartGenerator()
    chart_output = chart_gen.comparison_chart(days=days)
    console.print(chart_output)
    chart_gen.close()

# PDF EXPORT COMMANDS
@cli.group()
def pdf():
    """Generate PDF reports"""
    pass

@pdf.command()
@click.option('--filename', '-f', help='Custom filename')
@click.option('--charts/--no-charts', default=False, help='Include charts in report')
def weekly(filename, charts):
    """Generate weekly summary PDF report"""
    from agent.pdf_export import PDFExporter

    exporter = PDFExporter()
    pdf_path = exporter.export_weekly_report(filename=filename, include_charts=charts)

    console.print(f"[green]✓[/green] Weekly report generated:")
    console.print(f"  [cyan]{pdf_path}[/cyan]")

    exporter.close()

@pdf.command()
@click.option('--filename', '-f', help='Custom filename')
def monthly(filename):
    """Generate monthly summary PDF report"""
    from agent.pdf_export import PDFExporter

    exporter = PDFExporter()
    pdf_path = exporter.export_monthly_report(filename=filename)

    console.print(f"[green]✓[/green] Monthly report generated:")
    console.print(f"  [cyan]{pdf_path}[/cyan]")

    exporter.close()

@pdf.command()
@click.argument('goal_id', type=int)
@click.option('--filename', '-f', help='Custom filename')
def goal(goal_id, filename):
    """Generate PDF report for a specific goal"""
    from agent.pdf_export import PDFExporter

    exporter = PDFExporter()
    pdf_path = exporter.export_goal_report(goal_id, filename=filename)

    if pdf_path:
        console.print(f"[green]✓[/green] Goal report generated:")
        console.print(f"  [cyan]{pdf_path}[/cyan]")
    else:
        console.print(f"[red]✗[/red] Goal {goal_id} not found")

    exporter.close()

@pdf.command()
@click.option('--filename', '-f', help='Custom filename')
def all_goals(filename):
    """Generate PDF report for all active goals"""
    from agent.pdf_export import PDFExporter

    exporter = PDFExporter()
    pdf_path = exporter.export_all_goals_report(filename=filename)

    console.print(f"[green]✓[/green] All goals report generated:")
    console.print(f"  [cyan]{pdf_path}[/cyan]")

    exporter.close()

@pdf.command()
@click.option('--days', '-d', type=int, default=30, help='Number of days to analyze')
@click.option('--filename', '-f', help='Custom filename')
def velocity(days, filename):
    """Generate PDF velocity analysis report"""
    from agent.pdf_export import PDFExporter

    exporter = PDFExporter()
    pdf_path = exporter.export_velocity_report(days=days, filename=filename)

    console.print(f"[green]✓[/green] Velocity report generated:")
    console.print(f"  [cyan]{pdf_path}[/cyan]")

    exporter.close()

@pdf.command()
@click.argument('start_date')
@click.argument('end_date')
@click.option('--filename', '-f', help='Custom filename')
def daterange(start_date, end_date, filename):
    """Generate PDF report for custom date range (YYYY-MM-DD format)"""
    from agent.pdf_export import PDFExporter

    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        console.print("[red]✗[/red] Invalid date format. Use YYYY-MM-DD")
        return

    exporter = PDFExporter()
    pdf_path = exporter.export_date_range_report(start, end, filename=filename)

    console.print(f"[green]✓[/green] Date range report generated:")
    console.print(f"  [cyan]{pdf_path}[/cyan]")

    exporter.close()

# CALENDAR/EXPORT COMMANDS
@cli.group()
def calendar():
    """Calendar integration and exports"""
    pass

@calendar.command()
@click.option('--filter', '-f', type=click.Choice(['all', 'pending', 'today', 'week']), default='pending', help='Which tasks to export')
@click.option('--goal', '-g', type=int, help='Export tasks for specific goal only')
@click.option('--output', '-o', help='Output file path (default: ~/.business-agent/calendar/bizy_tasks.ics)')
def export(filter, goal, output):
    """Export tasks to iCalendar (.ics) file"""
    from agent.integrations.ical import ICalIntegration
    from agent.models import Task

    task_mgr = TaskManager()
    ical = ICalIntegration()

    # Get tasks based on filter
    if filter == 'all':
        if goal:
            tasks = task_mgr.session.query(Task).filter_by(parent_goal_id=goal).all()
        else:
            tasks = task_mgr.session.query(Task).all()
    elif filter == 'today':
        tasks = task_mgr.get_tasks_for_today()
    elif filter == 'week':
        # Get tasks due this week
        today = datetime.now()
        week_end = today + timedelta(days=7)
        query = task_mgr.session.query(Task).filter(Task.due_date <= week_end)
        if goal:
            query = query.filter_by(parent_goal_id=goal)
        tasks = query.all()
    else:  # pending
        query = task_mgr.session.query(Task).filter(Task.status.in_(['pending', 'in_progress']))
        if goal:
            query = query.filter_by(parent_goal_id=goal)
        tasks = query.all()

    if not tasks:
        console.print(f"[yellow]No {filter} tasks to export[/yellow]")
        task_mgr.close()
        return

    # Export tasks
    if output:
        from pathlib import Path
        ical.calendar_file = Path(output)

    calendar_path = ical.export_tasks(tasks)

    console.print(f"[green]✓[/green] Exported {len(tasks)} task(s) to:")
    console.print(f"  [cyan]{calendar_path}[/cyan]")
    console.print(f"\n[dim]Import this file into your calendar app:[/dim]")
    console.print(f"  • Apple Calendar: File → Import")
    console.print(f"  • Google Calendar: Settings → Import & export")
    console.print(f"  • Outlook: File → Open & Export → Import/Export")

    task_mgr.close()

@calendar.command()
@click.argument('task_id', type=int)
@click.option('--output', '-o', help='Output file path')
def export_task(task_id, output):
    """Export a single task as .ics file"""
    from agent.integrations.ical import ICalIntegration

    task_mgr = TaskManager()
    task = task_mgr.get_task(task_id)

    if not task:
        console.print(f"[red]✗[/red] Task {task_id} not found")
        task_mgr.close()
        return

    ical = ICalIntegration()
    calendar_path = ical.create_single_task_event(task, output)

    console.print(f"[green]✓[/green] Exported task to:")
    console.print(f"  [cyan]{calendar_path}[/cyan]")
    console.print(f"\n[dim]You can now:")
    console.print(f"  • Double-click the file to add it to your calendar")
    console.print(f"  • Drag and drop into your calendar app")

    task_mgr.close()

@calendar.command()
def path():
    """Show calendar export directory path"""
    from agent.integrations.ical import ICalIntegration

    ical = ICalIntegration()
    console.print(f"[cyan]Calendar files:[/cyan] {ical.calendar_dir}")
    console.print(f"[cyan]Main export:[/cyan] {ical.calendar_file}")

# DASHBOARD
@cli.command()
def dashboard():
    """Launch live dashboard (updates every 30s)"""
    from agent.dashboard import run_dashboard
    run_dashboard()

# DAILY/WEEKLY REVIEWS
@cli.command()
def brief():
    """Generate morning briefing"""
    from agent.morning_brief import run_morning_briefing
    run_morning_briefing()

@cli.command()
def review():
    """Generate evening review"""
    from agent.evening_review import run_evening_review
    run_evening_review()

@cli.command()
def weekly():
    """Generate weekly review"""
    from agent.weekly_review import run_weekly_review
    run_weekly_review()

# BUSINESS PLAN MANAGEMENT
@cli.group()
def plan():
    """Manage business plan"""
    pass

@plan.command()
def show():
    """Review current business plan and goals"""
    from agent.plan_manager import review_business_plan
    review_business_plan()

@plan.command()
def create():
    """Create new business plan"""
    from agent.plan_manager import create_business_plan
    create_business_plan()

@plan.command()
def update():
    """Update existing business plan"""
    from agent.plan_manager import update_business_plan
    update_business_plan()

@plan.command()
@click.argument('file_path', required=False)
@click.option('--name', '-n', help='Business plan name')
def load(file_path, name):
    """Load business plan from YAML file"""
    # Import and run the standalone script
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, repo_root)
    from scripts.load_business_plan import load_business_plan
    load_business_plan(file_path, name)

if __name__ == "__main__":
    cli()
