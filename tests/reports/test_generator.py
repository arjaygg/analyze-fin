# tests/reports/test_generator.py
"""Tests for ReportGenerator - HTML and Markdown report generation.

Tests cover:
- ReportGenerator class initialization
- HTML report generation
- Markdown report generation
- Template rendering
- File output handling
- Edge cases (limited data)
"""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from analyze_fin.analysis.spending import SpendingReport
from analyze_fin.reports.charts import ChartBuilder
from analyze_fin.reports.generator import (
    ReportGenerationError,
    ReportGenerator,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_spending_report() -> SpendingReport:
    """Create a sample SpendingReport for testing."""
    return SpendingReport(
        total_spent=Decimal("15000.50"),
        total_transactions=25,
        average_transaction=Decimal("600.02"),
        by_category={
            "Food & Dining": {
                "total": Decimal("5000.00"),
                "count": 10,
                "percentage": 33.33,
            },
            "Transportation": {
                "total": Decimal("3000.00"),
                "count": 8,
                "percentage": 20.00,
            },
            "Shopping": {
                "total": Decimal("7000.50"),
                "count": 7,
                "percentage": 46.67,
            },
        },
        by_month={
            "2024-10": {"total": Decimal("7000.00"), "count": 12},
            "2024-11": {"total": Decimal("8000.50"), "count": 13},
        },
        top_merchants=[
            {"merchant": "Jollibee", "total": Decimal("2000.00"), "count": 5},
            {"merchant": "Grab", "total": Decimal("1500.00"), "count": 6},
            {"merchant": "SM Supermarket", "total": Decimal("3500.00"), "count": 4},
        ],
    )


@pytest.fixture
def empty_spending_report() -> SpendingReport:
    """Create an empty SpendingReport for edge case testing."""
    return SpendingReport(
        total_spent=Decimal("0"),
        total_transactions=0,
        average_transaction=Decimal("0"),
        by_category={},
        by_month={},
        top_merchants=[],
    )


@pytest.fixture
def limited_data_report() -> SpendingReport:
    """Create a SpendingReport with limited data (< 10 transactions)."""
    return SpendingReport(
        total_spent=Decimal("500.00"),
        total_transactions=3,
        average_transaction=Decimal("166.67"),
        by_category={
            "Food & Dining": {
                "total": Decimal("500.00"),
                "count": 3,
                "percentage": 100.0,
            },
        },
        by_month={"2024-11": {"total": Decimal("500.00"), "count": 3}},
        top_merchants=[
            {"merchant": "Jollibee", "total": Decimal("500.00"), "count": 3},
        ],
    )


@pytest.fixture
def chart_builder() -> ChartBuilder:
    """Create a ChartBuilder instance."""
    return ChartBuilder()


@pytest.fixture
def report_generator() -> ReportGenerator:
    """Create a ReportGenerator instance."""
    return ReportGenerator()


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output_dir = tmp_path / "reports"
    output_dir.mkdir()
    return output_dir


# =============================================================================
# Task 1 Tests: ReportGenerator Structure
# =============================================================================


class TestReportGeneratorInit:
    """Tests for ReportGenerator initialization."""

    def test_creates_report_generator_instance(self) -> None:
        """Test that ReportGenerator can be instantiated."""
        generator = ReportGenerator()
        assert generator is not None
        assert isinstance(generator, ReportGenerator)

    def test_creates_with_custom_template_dir(self, tmp_path: Path) -> None:
        """Test ReportGenerator with custom template directory."""
        template_dir = tmp_path / "templates"
        template_dir.mkdir()

        generator = ReportGenerator(template_dir=template_dir)
        assert generator.template_dir == template_dir

    def test_creates_with_chart_builder(self, chart_builder: ChartBuilder) -> None:
        """Test ReportGenerator with injected ChartBuilder."""
        generator = ReportGenerator(chart_builder=chart_builder)
        assert generator.chart_builder is chart_builder

    def test_creates_default_chart_builder_if_not_provided(self) -> None:
        """Test that ReportGenerator creates default ChartBuilder."""
        generator = ReportGenerator()
        assert generator.chart_builder is not None
        assert isinstance(generator.chart_builder, ChartBuilder)


# =============================================================================
# Task 2 Tests: HTML Report Generation
# =============================================================================


class TestHTMLReportGeneration:
    """Tests for HTML report generation."""

    def test_generates_html_report(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test generating HTML report from SpendingReport."""
        html = report_generator.generate_html(sample_spending_report)

        assert html is not None
        assert isinstance(html, str)
        assert len(html) > 0

    def test_html_report_contains_doctype(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test that HTML report starts with DOCTYPE."""
        html = report_generator.generate_html(sample_spending_report)
        assert html.strip().startswith("<!DOCTYPE html>")

    def test_html_report_contains_title(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test that HTML report contains a title."""
        html = report_generator.generate_html(sample_spending_report)
        assert "<title>" in html
        assert "Spending Report" in html

    def test_html_report_contains_summary_section(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test HTML report contains summary statistics."""
        html = report_generator.generate_html(sample_spending_report)

        # Total spending
        assert "₱15,000.50" in html or "15,000.50" in html
        # Transaction count
        assert "25" in html
        # Average should appear
        assert "600" in html

    def test_html_report_contains_category_section(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test HTML report contains category breakdown."""
        html = report_generator.generate_html(sample_spending_report)

        assert "Food & Dining" in html
        assert "Transportation" in html
        assert "Shopping" in html

    def test_html_report_contains_merchant_section(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test HTML report contains top merchants."""
        html = report_generator.generate_html(sample_spending_report)

        assert "Jollibee" in html
        assert "Grab" in html
        assert "SM Supermarket" in html

    def test_html_report_embeds_charts(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test HTML report contains embedded Plotly charts."""
        html = report_generator.generate_html(sample_spending_report)

        # Plotly CDN should be referenced
        assert "plotly" in html.lower()

    def test_html_report_with_custom_title(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test HTML report with custom title."""
        html = report_generator.generate_html(
            sample_spending_report,
            title="November 2024 Spending Report",
        )
        assert "November 2024 Spending Report" in html

    def test_html_report_with_date_range(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test HTML report includes date range."""
        start = datetime(2024, 11, 1)
        end = datetime(2024, 11, 30)

        html = report_generator.generate_html(
            sample_spending_report,
            start_date=start,
            end_date=end,
        )

        # Date range should appear in report
        assert "Nov" in html
        assert "2024" in html


# =============================================================================
# Task 3 Tests: Markdown Report Generation
# =============================================================================


class TestMarkdownReportGeneration:
    """Tests for Markdown report generation."""

    def test_generates_markdown_report(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test generating Markdown report from SpendingReport."""
        md = report_generator.generate_markdown(sample_spending_report)

        assert md is not None
        assert isinstance(md, str)
        assert len(md) > 0

    def test_markdown_report_contains_header(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test that Markdown report starts with header."""
        md = report_generator.generate_markdown(sample_spending_report)
        assert md.startswith("#")

    def test_markdown_report_contains_summary(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test Markdown report contains summary statistics."""
        md = report_generator.generate_markdown(sample_spending_report)

        # Check for summary values
        assert "15,000.50" in md or "₱15,000.50" in md
        assert "25" in md  # transaction count

    def test_markdown_report_contains_tables(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test Markdown report uses tables for data."""
        md = report_generator.generate_markdown(sample_spending_report)

        # Markdown table syntax
        assert "|" in md
        assert "---" in md or "|-" in md

    def test_markdown_report_contains_categories(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test Markdown report contains category breakdown."""
        md = report_generator.generate_markdown(sample_spending_report)

        assert "Food & Dining" in md
        assert "Transportation" in md
        assert "Shopping" in md

    def test_markdown_report_readable_in_text_editor(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
    ) -> None:
        """Test Markdown is readable without rendering (no binary/HTML)."""
        md = report_generator.generate_markdown(sample_spending_report)

        # Should not contain HTML tags (except maybe inline)
        assert "<!DOCTYPE" not in md
        assert "<script>" not in md


# =============================================================================
# Task 4 Tests: File Output Handling
# =============================================================================


class TestFileOutputHandling:
    """Tests for report file saving."""

    def test_saves_html_report_to_file(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
        temp_output_dir: Path,
    ) -> None:
        """Test saving HTML report to file."""
        html = report_generator.generate_html(sample_spending_report)
        output_path = temp_output_dir / "report.html"

        report_generator.save_report(html, output_path)

        assert output_path.exists()
        assert output_path.read_text() == html

    def test_saves_markdown_report_to_file(
        self,
        report_generator: ReportGenerator,
        sample_spending_report: SpendingReport,
        temp_output_dir: Path,
    ) -> None:
        """Test saving Markdown report to file."""
        md = report_generator.generate_markdown(sample_spending_report)
        output_path = temp_output_dir / "report.md"

        report_generator.save_report(md, output_path)

        assert output_path.exists()
        assert output_path.read_text() == md

    def test_generates_default_filename_with_date(
        self,
        report_generator: ReportGenerator,
    ) -> None:
        """Test default filename includes date."""
        filename = report_generator.get_default_filename(format="html")

        # Should be like spending_report_2024_11_30.html
        assert filename.startswith("spending_report_")
        assert filename.endswith(".html")
        assert "_" in filename

    def test_generates_default_filename_markdown(
        self,
        report_generator: ReportGenerator,
    ) -> None:
        """Test default filename for markdown format."""
        filename = report_generator.get_default_filename(format="markdown")

        assert filename.endswith(".md")

    def test_prevents_overwrite_by_default(
        self,
        report_generator: ReportGenerator,
        temp_output_dir: Path,
    ) -> None:
        """Test that existing files are not overwritten by default."""
        output_path = temp_output_dir / "existing_report.html"
        output_path.write_text("existing content")

        with pytest.raises(FileExistsError):
            report_generator.save_report("new content", output_path, overwrite=False)

    def test_allows_overwrite_when_forced(
        self,
        report_generator: ReportGenerator,
        temp_output_dir: Path,
    ) -> None:
        """Test that files can be overwritten when forced."""
        output_path = temp_output_dir / "existing_report.html"
        output_path.write_text("existing content")

        report_generator.save_report("new content", output_path, overwrite=True)

        assert output_path.read_text() == "new content"

    def test_creates_parent_directories(
        self,
        report_generator: ReportGenerator,
        temp_output_dir: Path,
    ) -> None:
        """Test that parent directories are created if they don't exist."""
        output_path = temp_output_dir / "subdir" / "nested" / "report.html"

        report_generator.save_report("content", output_path)

        assert output_path.exists()


# =============================================================================
# Task 5 Tests: Edge Cases & Error Handling
# =============================================================================


class TestLimitedDataHandling:
    """Tests for reports with limited/insufficient data."""

    def test_html_report_with_empty_data(
        self,
        report_generator: ReportGenerator,
        empty_spending_report: SpendingReport,
    ) -> None:
        """Test HTML report generation with empty data."""
        html = report_generator.generate_html(empty_spending_report)

        assert html is not None
        assert "<!DOCTYPE html>" in html
        # Should not throw error

    def test_markdown_report_with_empty_data(
        self,
        report_generator: ReportGenerator,
        empty_spending_report: SpendingReport,
    ) -> None:
        """Test Markdown report generation with empty data."""
        md = report_generator.generate_markdown(empty_spending_report)

        assert md is not None
        assert "#" in md

    def test_html_report_shows_limited_data_warning(
        self,
        report_generator: ReportGenerator,
        limited_data_report: SpendingReport,
    ) -> None:
        """Test HTML report shows warning for limited data."""
        html = report_generator.generate_html(limited_data_report)

        # Should contain warning about limited data
        assert "limited" in html.lower() or "warning" in html.lower()

    def test_markdown_report_shows_limited_data_warning(
        self,
        report_generator: ReportGenerator,
        limited_data_report: SpendingReport,
    ) -> None:
        """Test Markdown report shows warning for limited data."""
        md = report_generator.generate_markdown(limited_data_report)

        # Should contain warning about limited data
        assert "limited" in md.lower() or "warning" in md.lower()


class TestErrorHandling:
    """Tests for error handling in report generation."""

    def test_raises_error_for_invalid_format(
        self,
        report_generator: ReportGenerator,
    ) -> None:
        """Test that invalid format raises error."""
        with pytest.raises(ValueError):
            report_generator.get_default_filename(format="invalid")

    def test_raises_error_for_template_not_found(self) -> None:
        """Test that missing template raises ReportGenerationError."""
        # Create generator with non-existent template dir
        generator = ReportGenerator(template_dir=Path("/nonexistent/templates"))

        # Creating a basic report should raise error
        report = SpendingReport(
            total_spent=Decimal("100"),
            total_transactions=1,
            average_transaction=Decimal("100"),
            by_category={},
            by_month={},
            top_merchants=[],
        )

        with pytest.raises(ReportGenerationError):
            generator.generate_html(report)


# =============================================================================
# Integration Tests
# =============================================================================


class TestReportGeneratorIntegration:
    """Integration tests for full report generation flow."""

    def test_full_html_report_flow(
        self,
        sample_spending_report: SpendingReport,
        temp_output_dir: Path,
    ) -> None:
        """Test complete HTML report generation and save flow."""
        generator = ReportGenerator()

        # Generate HTML
        html = generator.generate_html(
            sample_spending_report,
            title="Test Report",
        )

        # Get default filename
        filename = generator.get_default_filename(format="html")
        output_path = temp_output_dir / filename

        # Save
        generator.save_report(html, output_path)

        # Verify
        assert output_path.exists()
        content = output_path.read_text()
        assert "Test Report" in content
        assert "₱15,000.50" in content or "15,000.50" in content

    def test_full_markdown_report_flow(
        self,
        sample_spending_report: SpendingReport,
        temp_output_dir: Path,
    ) -> None:
        """Test complete Markdown report generation and save flow."""
        generator = ReportGenerator()

        # Generate Markdown
        md = generator.generate_markdown(sample_spending_report)

        # Get default filename
        filename = generator.get_default_filename(format="markdown")
        output_path = temp_output_dir / filename

        # Save
        generator.save_report(md, output_path)

        # Verify
        assert output_path.exists()
        content = output_path.read_text()
        assert "#" in content
        assert "|" in content  # Tables
