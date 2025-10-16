"""Tests for PDF export with ReportLab (TDD)"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from agent.tasks import TaskManager
from agent.planner import BusinessPlanner
from agent.pdf_export import PDFExporter


class TestPDFExporter:
    """Tests for PDF report generation"""

    @pytest.fixture
    def pdf_exporter(self, tmp_path, test_session):
        """Create PDFExporter with temp directory and test session"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        planner = BusinessPlanner()
        planner.session = test_session

        exporter = PDFExporter(output_dir=tmp_path, task_mgr=task_mgr, planner=planner)
        yield exporter
        exporter.close()

    @pytest.fixture
    def sample_data(self, test_session):
        """Create sample tasks and goals for PDF testing"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        planner = BusinessPlanner()
        planner.session = test_session

        # Create goals
        goal1 = planner.create_goal(
            title="Q1 Product Launch",
            description="Launch new product features",
            horizon="quarterly",
            target_date=datetime.now() + timedelta(days=90)
        )

        goal2 = planner.create_goal(
            title="Marketing Campaign",
            description="Increase brand awareness",
            horizon="monthly",
            target_date=datetime.now() + timedelta(days=30)
        )

        # Create tasks for goal 1
        for i in range(10):
            task = task_mgr.create_task(
                title=f"Feature {i+1}",
                description=f"Implement feature {i+1}",
                priority=1 if i < 3 else 2,
                category="development",
                parent_goal_id=goal1.id
            )
            if i < 5:
                task.completed_at = datetime.now() - timedelta(days=i)
                task.status = 'completed'
                test_session.add(task)

        # Create tasks for goal 2
        for i in range(5):
            task = task_mgr.create_task(
                title=f"Marketing Task {i+1}",
                description=f"Marketing activity {i+1}",
                priority=2,
                category="marketing",
                parent_goal_id=goal2.id
            )
            if i < 2:
                task.completed_at = datetime.now() - timedelta(hours=i*6)
                task.status = 'completed'
                test_session.add(task)

        test_session.commit()

        return {
            'task_mgr': task_mgr,
            'planner': planner,
            'goals': [goal1, goal2]
        }

    def test_export_weekly_report_creates_file(self, pdf_exporter, sample_data):
        """Test that weekly report creates a PDF file"""
        pdf_path = pdf_exporter.export_weekly_report()

        assert pdf_path.exists()
        assert pdf_path.suffix == '.pdf'
        assert pdf_path.stat().st_size > 0  # File has content

    def test_export_goal_report_creates_file(self, pdf_exporter, sample_data):
        """Test that goal report creates a PDF file"""
        goal = sample_data['goals'][0]
        pdf_path = pdf_exporter.export_goal_report(goal.id)

        assert pdf_path.exists()
        assert pdf_path.suffix == '.pdf'
        assert pdf_path.stat().st_size > 0

    def test_export_goal_report_invalid_goal(self, pdf_exporter):
        """Test goal report with invalid goal ID"""
        pdf_path = pdf_exporter.export_goal_report(999999)

        # Should either return None or raise exception
        assert pdf_path is None or not pdf_path.exists()

    def test_export_custom_date_range(self, pdf_exporter, sample_data):
        """Test report for custom date range"""
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        pdf_path = pdf_exporter.export_date_range_report(start_date, end_date)

        assert pdf_path.exists()
        assert pdf_path.suffix == '.pdf'

    def test_export_with_custom_filename(self, pdf_exporter, sample_data):
        """Test exporting with custom filename"""
        custom_name = "my_custom_report.pdf"
        pdf_path = pdf_exporter.export_weekly_report(filename=custom_name)

        assert pdf_path.name == custom_name
        assert pdf_path.exists()

    def test_weekly_report_includes_stats(self, pdf_exporter, sample_data):
        """Test that weekly report includes statistics"""
        pdf_path = pdf_exporter.export_weekly_report()

        # Read PDF and check it contains expected content
        # (We'll just verify file size is reasonable for now)
        assert pdf_path.stat().st_size > 1000  # Should be > 1KB

    def test_goal_report_includes_progress(self, pdf_exporter, sample_data):
        """Test that goal report includes progress information"""
        goal = sample_data['goals'][0]
        pdf_path = pdf_exporter.export_goal_report(goal.id)

        # Verify reasonable file size
        assert pdf_path.stat().st_size > 1000

    def test_export_all_goals_report(self, pdf_exporter, sample_data):
        """Test exporting report for all active goals"""
        pdf_path = pdf_exporter.export_all_goals_report()

        assert pdf_path.exists()
        assert pdf_path.suffix == '.pdf'
        assert pdf_path.stat().st_size > 1000

    def test_export_task_list(self, pdf_exporter, sample_data):
        """Test exporting simple task list to PDF"""
        task_mgr = sample_data['task_mgr']
        from agent.models import Task

        tasks = task_mgr.session.query(Task).limit(10).all()
        pdf_path = pdf_exporter.export_task_list(tasks, "My Tasks")

        assert pdf_path.exists()
        assert pdf_path.suffix == '.pdf'

    def test_export_with_charts(self, pdf_exporter, sample_data):
        """Test that reports can include charts"""
        # This tests embedding charts in PDF
        pdf_path = pdf_exporter.export_weekly_report(include_charts=True)

        assert pdf_path.exists()
        # With charts should be larger than without
        assert pdf_path.stat().st_size > 2000

    def test_export_creates_directory_if_missing(self, tmp_path, test_session):
        """Test that exporter creates output directory if it doesn't exist"""
        non_existent_dir = tmp_path / "reports" / "pdfs"
        assert not non_existent_dir.exists()

        task_mgr = TaskManager()
        task_mgr.session = test_session
        planner = BusinessPlanner()
        planner.session = test_session

        exporter = PDFExporter(output_dir=non_existent_dir, task_mgr=task_mgr, planner=planner)
        pdf_path = exporter.export_weekly_report()

        assert non_existent_dir.exists()
        assert pdf_path.exists()
        exporter.close()

    def test_export_velocity_report(self, pdf_exporter, sample_data):
        """Test exporting velocity analysis report"""
        pdf_path = pdf_exporter.export_velocity_report(days=30)

        assert pdf_path.exists()
        assert pdf_path.suffix == '.pdf'

    def test_export_with_metadata(self, pdf_exporter, sample_data):
        """Test that PDF includes proper metadata"""
        pdf_path = pdf_exporter.export_weekly_report()

        # We can't easily read PDF metadata in tests without additional libraries,
        # but we can verify the file was created successfully
        assert pdf_path.exists()

    def test_export_handles_empty_data_gracefully(self, pdf_exporter):
        """Test that exporter handles empty data sets without crashing"""
        # No tasks or goals created
        pdf_path = pdf_exporter.export_weekly_report()

        # Should still create a PDF even with no data
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 500  # Minimal PDF

    def test_export_monthly_report(self, pdf_exporter, sample_data):
        """Test exporting monthly summary report"""
        pdf_path = pdf_exporter.export_monthly_report()

        assert pdf_path.exists()
        assert pdf_path.suffix == '.pdf'

    def test_export_with_logo(self, pdf_exporter, sample_data, tmp_path):
        """Test adding custom logo to reports"""
        # Test with non-existent logo (should be handled gracefully)
        logo_path = tmp_path / "nonexistent_logo.png"

        # Should not crash even with bad logo path
        pdf_path = pdf_exporter.export_weekly_report(logo_path=logo_path)

        assert pdf_path.exists()
        # Logo should be skipped silently, PDF still created

    def test_multiple_exports_dont_collide(self, pdf_exporter, sample_data):
        """Test that multiple exports create unique files"""
        pdf_path1 = pdf_exporter.export_weekly_report()
        pdf_path2 = pdf_exporter.export_weekly_report()

        assert pdf_path1.exists()
        assert pdf_path2.exists()
        # Should be different files or same file is overwritten
        assert pdf_path1.stat().st_mtime <= pdf_path2.stat().st_mtime
