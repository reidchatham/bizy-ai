"""PDF Export for Bizy AI using ReportLab

Generates professional PDF reports:
- Weekly/Monthly summaries
- Goal progress reports
- Task lists
- Velocity analysis
- Charts and visualizations
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from agent.tasks import TaskManager
from agent.planner import BusinessPlanner
from agent.models import Task, Goal


class PDFExporter:
    """Generate PDF reports using ReportLab"""

    def __init__(self, output_dir: Optional[Path] = None, task_mgr: Optional[TaskManager] = None, planner: Optional[BusinessPlanner] = None):
        """Initialize PDF exporter

        Args:
            output_dir: Directory for PDF outputs (default: ~/.business-agent/reports/)
            task_mgr: Optional TaskManager instance (for testing)
            planner: Optional BusinessPlanner instance (for testing)
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            home = Path.home()
            self.output_dir = home / ".business-agent" / "reports"

        # Create directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.task_mgr = task_mgr if task_mgr else TaskManager()
        self.planner = planner if planner else BusinessPlanner()
        self._owns_managers = task_mgr is None and planner is None  # Only close if we created them
        self.styles = getSampleStyleSheet()

        # Create custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=12,
            spaceBefore=12
        )

    def close(self):
        """Close database connections"""
        if self._owns_managers:
            self.task_mgr.close()
            self.planner.close()

    def _create_pdf_doc(self, filename: str) -> tuple:
        """Create PDF document and story list

        Args:
            filename: PDF filename

        Returns:
            Tuple of (doc, story)
        """
        pdf_path = self.output_dir / filename
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        story = []
        return doc, story, pdf_path

    def _add_header(self, story: list, title: str, date_str: Optional[str] = None):
        """Add report header

        Args:
            story: Story list to append to
            title: Report title
            date_str: Optional date string
        """
        story.append(Paragraph(title, self.title_style))

        if date_str is None:
            date_str = datetime.now().strftime('%B %d, %Y')

        story.append(Paragraph(f"Generated: {date_str}", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

    def _add_stats_table(self, story: list, stats: dict):
        """Add statistics table to report

        Args:
            story: Story list to append to
            stats: Statistics dictionary
        """
        data = [
            ['Metric', 'Value'],
            ['Tasks Completed', str(stats.get('tasks_completed', 0))],
            ['Tasks Created', str(stats.get('tasks_created', 0))],
            ['Completion Rate', f"{stats.get('completion_rate', 0):.1f}%"],
            ['Velocity', f"{stats.get('velocity', 0):.1f} tasks/day"],
        ]

        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(table)
        story.append(Spacer(1, 0.3*inch))

    def _add_task_table(self, story: list, tasks: List[Task], title: str = "Tasks"):
        """Add task list table to report

        Args:
            story: Story list to append to
            tasks: List of tasks
            title: Table title
        """
        story.append(Paragraph(title, self.heading_style))

        if not tasks:
            story.append(Paragraph("No tasks found", self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            return

        data = [['Status', 'Priority', 'Title', 'Category']]

        for task in tasks[:20]:  # Limit to 20 tasks per table
            status = '✓' if task.status == 'completed' else '○'
            priority = str(task.priority) if task.priority else '3'
            title_short = task.title[:40] + '...' if len(task.title) > 40 else task.title
            category = task.category or '-'

            data.append([status, priority, title_short, category])

        table = Table(data, colWidths=[0.5*inch, 0.7*inch, 3.5*inch, 1.3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))

        story.append(table)
        story.append(Spacer(1, 0.3*inch))

    def _add_goal_progress(self, story: list, goal: Goal):
        """Add goal progress section

        Args:
            story: Story list to append to
            goal: Goal object
        """
        story.append(Paragraph(f"Goal: {goal.title}", self.heading_style))
        story.append(Paragraph(f"Progress: {goal.progress_percentage:.1f}%", self.styles['Normal']))

        if goal.description:
            story.append(Paragraph(f"<i>{goal.description}</i>", self.styles['Normal']))

        if goal.target_date:
            story.append(Paragraph(
                f"Target Date: {goal.target_date.strftime('%Y-%m-%d')}",
                self.styles['Normal']
            ))

        story.append(Spacer(1, 0.2*inch))

    def export_weekly_report(
        self,
        filename: Optional[str] = None,
        include_charts: bool = False,
        logo_path: Optional[Path] = None
    ) -> Path:
        """Export weekly summary report

        Args:
            filename: Optional custom filename
            include_charts: Whether to include charts
            logo_path: Optional path to logo image

        Returns:
            Path to created PDF file
        """
        if filename is None:
            filename = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.pdf"

        doc, story, pdf_path = self._create_pdf_doc(filename)

        # Add header
        self._add_header(story, "Weekly Report")

        # Add logo if provided
        if logo_path and logo_path.exists():
            try:
                logo = RLImage(str(logo_path), width=1*inch, height=1*inch)
                story.append(logo)
                story.append(Spacer(1, 0.2*inch))
            except:
                pass  # Skip if logo can't be loaded

        # Get weekly stats
        weekly_stats = self.task_mgr.get_weekly_task_stats()
        velocity = self.task_mgr.get_task_velocity(days=7)

        stats = {
            'tasks_completed': weekly_stats['tasks_completed_this_week'],
            'tasks_created': weekly_stats['tasks_created_this_week'],
            'completion_rate': weekly_stats['completion_rate'],
            'velocity': velocity
        }

        self._add_stats_table(story, stats)

        # Add completed tasks
        week_start = datetime.now() - timedelta(days=7)
        completed_tasks = self.task_mgr.session.query(Task).filter(
            Task.status == 'completed',
            Task.completed_at >= week_start
        ).all()

        self._add_task_table(story, completed_tasks, "Completed This Week")

        # Add pending tasks
        pending_tasks = self.task_mgr.session.query(Task).filter(
            Task.status.in_(['pending', 'in_progress'])
        ).limit(20).all()

        self._add_task_table(story, pending_tasks, "Pending Tasks")

        # Build PDF
        doc.build(story)
        return pdf_path

    def export_goal_report(self, goal_id: int, filename: Optional[str] = None) -> Optional[Path]:
        """Export report for specific goal

        Args:
            goal_id: Goal ID
            filename: Optional custom filename

        Returns:
            Path to created PDF or None if goal not found
        """
        goal = self.planner.get_goal(goal_id)
        if not goal:
            return None

        if filename is None:
            safe_title = "".join(c for c in goal.title if c.isalnum() or c in (' ', '-', '_'))
            filename = f"goal_{safe_title[:30]}_{datetime.now().strftime('%Y%m%d')}.pdf"

        doc, story, pdf_path = self._create_pdf_doc(filename)

        # Add header
        self._add_header(story, f"Goal Report: {goal.title}")

        # Add goal details
        self._add_goal_progress(story, goal)

        # Get tasks for this goal
        all_tasks = self.task_mgr.session.query(Task).filter(
            Task.parent_goal_id == goal_id
        ).all()

        completed_tasks = [t for t in all_tasks if t.status == 'completed']
        pending_tasks = [t for t in all_tasks if t.status in ['pending', 'in_progress']]

        # Add task tables
        self._add_task_table(story, completed_tasks, "Completed Tasks")
        self._add_task_table(story, pending_tasks, "Pending Tasks")

        # Build PDF
        doc.build(story)
        return pdf_path

    def export_all_goals_report(self, filename: Optional[str] = None) -> Path:
        """Export report for all active goals

        Args:
            filename: Optional custom filename

        Returns:
            Path to created PDF
        """
        if filename is None:
            filename = f"all_goals_{datetime.now().strftime('%Y%m%d')}.pdf"

        doc, story, pdf_path = self._create_pdf_doc(filename)

        # Add header
        self._add_header(story, "All Active Goals")

        goals = self.planner.get_active_goals()

        if not goals:
            story.append(Paragraph("No active goals found", self.styles['Normal']))
        else:
            for goal in goals:
                self._add_goal_progress(story, goal)

                # Get task count for this goal
                task_count = self.task_mgr.session.query(Task).filter(
                    Task.parent_goal_id == goal.id
                ).count()

                completed_count = self.task_mgr.session.query(Task).filter(
                    Task.parent_goal_id == goal.id,
                    Task.status == 'completed'
                ).count()

                story.append(Paragraph(
                    f"Tasks: {completed_count}/{task_count} completed",
                    self.styles['Normal']
                ))
                story.append(Spacer(1, 0.3*inch))

        # Build PDF
        doc.build(story)
        return pdf_path

    def export_task_list(
        self,
        tasks: List[Task],
        title: str = "Task List",
        filename: Optional[str] = None
    ) -> Path:
        """Export simple task list to PDF

        Args:
            tasks: List of tasks
            title: Report title
            filename: Optional custom filename

        Returns:
            Path to created PDF
        """
        if filename is None:
            filename = f"task_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        doc, story, pdf_path = self._create_pdf_doc(filename)

        # Add header
        self._add_header(story, title)

        # Add task table
        self._add_task_table(story, tasks, f"{len(tasks)} Tasks")

        # Build PDF
        doc.build(story)
        return pdf_path

    def export_date_range_report(
        self,
        start_date: datetime,
        end_date: datetime,
        filename: Optional[str] = None
    ) -> Path:
        """Export report for custom date range

        Args:
            start_date: Start date
            end_date: End date
            filename: Optional custom filename

        Returns:
            Path to created PDF
        """
        if filename is None:
            filename = f"report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"

        doc, story, pdf_path = self._create_pdf_doc(filename)

        # Add header
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        self._add_header(story, "Date Range Report", date_range)

        # Get tasks in date range
        completed_tasks = self.task_mgr.session.query(Task).filter(
            Task.status == 'completed',
            Task.completed_at >= start_date,
            Task.completed_at <= end_date
        ).all()

        # Calculate stats
        velocity = len(completed_tasks) / max(1, (end_date - start_date).days)
        stats = {
            'tasks_completed': len(completed_tasks),
            'tasks_created': 0,  # Would need to track creation date
            'completion_rate': 100.0,  # Only showing completed
            'velocity': velocity
        }

        self._add_stats_table(story, stats)
        self._add_task_table(story, completed_tasks, "Completed Tasks")

        # Build PDF
        doc.build(story)
        return pdf_path

    def export_velocity_report(self, days: int = 30, filename: Optional[str] = None) -> Path:
        """Export velocity analysis report

        Args:
            days: Number of days to analyze
            filename: Optional custom filename

        Returns:
            Path to created PDF
        """
        if filename is None:
            filename = f"velocity_report_{datetime.now().strftime('%Y%m%d')}.pdf"

        doc, story, pdf_path = self._create_pdf_doc(filename)

        # Add header
        self._add_header(story, f"Velocity Analysis ({days} days)")

        # Calculate velocity
        velocity = self.task_mgr.get_task_velocity(days=days)

        # Get completed tasks
        start_date = datetime.now() - timedelta(days=days)
        completed_tasks = self.task_mgr.session.query(Task).filter(
            Task.status == 'completed',
            Task.completed_at >= start_date
        ).all()

        stats = {
            'tasks_completed': len(completed_tasks),
            'tasks_created': 0,
            'completion_rate': 100.0,
            'velocity': velocity
        }

        self._add_stats_table(story, stats)

        # Add insight
        story.append(Paragraph(
            f"Average velocity over the last {days} days: {velocity:.2f} tasks per day",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))

        self._add_task_table(story, completed_tasks, f"Completed in Last {days} Days")

        # Build PDF
        doc.build(story)
        return pdf_path

    def export_monthly_report(self, filename: Optional[str] = None) -> Path:
        """Export monthly summary report

        Args:
            filename: Optional custom filename

        Returns:
            Path to created PDF
        """
        if filename is None:
            filename = f"monthly_report_{datetime.now().strftime('%Y%m')}.pdf"

        # Use 30 days as approximation of month
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        return self.export_date_range_report(start_date, end_date, filename)
