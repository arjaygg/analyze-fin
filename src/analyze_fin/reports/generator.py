# src/analyze_fin/reports/generator.py
"""Report generation using Jinja2 templates.

This module provides the ReportGenerator class for creating HTML and Markdown
reports from spending analysis data. Reports include embedded Plotly charts
for HTML output and markdown tables for text output.

Example:
    generator = ReportGenerator()
    html = generator.generate_html(spending_report, title="November Report")
    generator.save_report(html, Path("report.html"))
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from analyze_fin.exceptions import ReportGenerationError
from analyze_fin.reports.charts import ChartBuilder

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from analyze_fin.analysis.spending import SpendingReport

# Threshold for "limited data" warning
MIN_TRANSACTIONS_FOR_INSIGHTS = 10

# Default template directory (relative to package root)
DEFAULT_TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "templates" / "reports"


def _format_currency(amount: Decimal | float) -> str:
    """Format amount as Philippine Peso currency.

    Args:
        amount: Amount to format.

    Returns:
        Formatted string like "₱12,345.67"
    """
    if isinstance(amount, Decimal):
        amount = float(amount)
    return f"₱{amount:,.2f}"


def _format_date_display(dt: datetime | date) -> str:
    """Format date for display in reports.

    Args:
        dt: Date or datetime to format.

    Returns:
        Formatted string like "Nov 15, 2024"
    """
    if isinstance(dt, datetime):
        dt = dt.date()
    return dt.strftime("%b %d, %Y")


def _format_date_for_filename(dt: datetime | date) -> str:
    """Format date for use in filenames.

    Args:
        dt: Date or datetime to format.

    Returns:
        Formatted string like "2024_11_15"
    """
    if isinstance(dt, datetime):
        dt = dt.date()
    return dt.strftime("%Y_%m_%d")


class ReportGenerator:
    """Generate HTML and Markdown reports from spending analysis data.

    ReportGenerator uses Jinja2 templates to render reports with embedded
    charts (for HTML) or tables (for Markdown). Reports include summary
    statistics, category breakdowns, top merchants, and spending trends.

    Attributes:
        template_dir: Directory containing Jinja2 templates.
        chart_builder: ChartBuilder instance for generating charts.
        env: Jinja2 Environment for template rendering.

    Example:
        generator = ReportGenerator()

        # Generate HTML report
        html = generator.generate_html(
            spending_report,
            title="November 2024 Spending Report",
            start_date=datetime(2024, 11, 1),
            end_date=datetime(2024, 11, 30),
        )

        # Save to file
        generator.save_report(html, Path("reports/november.html"))

        # Generate Markdown
        md = generator.generate_markdown(spending_report)
        generator.save_report(md, Path("reports/november.md"))
    """

    def __init__(
        self,
        template_dir: Path | None = None,
        chart_builder: ChartBuilder | None = None,
    ) -> None:
        """Initialize ReportGenerator.

        Args:
            template_dir: Directory containing Jinja2 templates.
                Defaults to templates/reports/ in package root.
            chart_builder: ChartBuilder instance for chart generation.
                Creates default instance if not provided.
        """
        self.template_dir = template_dir or DEFAULT_TEMPLATE_DIR
        self.chart_builder = chart_builder or ChartBuilder()

        # Set up Jinja2 environments
        # HTML environment with autoescaping for security
        self._html_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True,  # Security: escape HTML by default
        )
        self._html_env.filters["currency"] = _format_currency
        self._html_env.filters["date_display"] = _format_date_display

        # Markdown environment without autoescaping
        self._md_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False,  # No escaping for markdown
        )
        self._md_env.filters["currency"] = _format_currency
        self._md_env.filters["date_display"] = _format_date_display

        # Keep env for backwards compat (points to HTML env)
        self.env = self._html_env

    def generate_html(
        self,
        report: "SpendingReport",
        title: str = "Spending Report",
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        notes: str | None = None,
    ) -> str:
        """Generate HTML report with embedded Plotly charts.

        Creates a complete HTML document with summary statistics, category
        breakdown, top merchants, and spending trends. Charts are embedded
        as interactive Plotly visualizations.

        Args:
            report: SpendingReport from SpendingAnalyzer.analyze().
            title: Report title. Defaults to "Spending Report".
            start_date: Optional start date for date range display.
            end_date: Optional end date for date range display.
            notes: Optional notes to include in report.

        Returns:
            Complete HTML document as string.

        Raises:
            ReportGenerationError: If template is not found or rendering fails.
        """
        try:
            template = self._html_env.get_template("dashboard.html.j2")
        except TemplateNotFound as e:
            raise ReportGenerationError(
                f"HTML template not found: {e}",
                template="dashboard.html.j2",
                format="html",
            ) from e

        # Generate charts
        charts = self.chart_builder.generate_all_charts(report)

        # Warn if all charts are empty (insufficient data for visualization)
        if all(not chart_html for chart_html in charts.values()):
            logger.warning(
                "All charts are empty - insufficient data for visualization. "
                "Consider importing more transactions before generating reports."
            )

        # Check for limited data
        has_limited_data = report.total_transactions < MIN_TRANSACTIONS_FOR_INSIGHTS

        # Build template context
        context = {
            "title": title,
            "report": report,
            "charts": charts,
            "start_date": start_date,
            "end_date": end_date,
            "notes": notes,
            "has_limited_data": has_limited_data,
            "generated_at": datetime.now(),
            # Formatted values for display
            "total_spent_formatted": _format_currency(report.total_spent),
            "average_formatted": _format_currency(report.average_transaction),
            # Sorted categories by amount
            "categories_sorted": sorted(
                report.by_category.items(),
                key=lambda x: float(x[1]["total"]),
                reverse=True,
            ),
            # Sorted merchants by amount
            "merchants_sorted": sorted(
                report.top_merchants,
                key=lambda x: float(x["total"]),
                reverse=True,
            ),
        }

        try:
            return template.render(**context)
        except Exception as e:
            raise ReportGenerationError(
                f"Failed to render HTML template: {e}",
                template="dashboard.html.j2",
                format="html",
            ) from e

    def generate_markdown(
        self,
        report: "SpendingReport",
        title: str = "Spending Report",
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        notes: str | None = None,
    ) -> str:
        """Generate Markdown report with tables.

        Creates a Markdown document with summary statistics, category
        breakdown, and top merchants in table format. Readable in text
        editors and renders well on GitHub.

        Args:
            report: SpendingReport from SpendingAnalyzer.analyze().
            title: Report title. Defaults to "Spending Report".
            start_date: Optional start date for date range display.
            end_date: Optional end date for date range display.
            notes: Optional notes to include in report.

        Returns:
            Markdown document as string.

        Raises:
            ReportGenerationError: If template is not found or rendering fails.
        """
        try:
            template = self._md_env.get_template("summary.md.j2")
        except TemplateNotFound as e:
            raise ReportGenerationError(
                f"Markdown template not found: {e}",
                template="summary.md.j2",
                format="markdown",
            ) from e

        # Check for limited data
        has_limited_data = report.total_transactions < MIN_TRANSACTIONS_FOR_INSIGHTS

        # Build template context
        context = {
            "title": title,
            "report": report,
            "start_date": start_date,
            "end_date": end_date,
            "notes": notes,
            "has_limited_data": has_limited_data,
            "generated_at": datetime.now(),
            # Formatted values for display
            "total_spent_formatted": _format_currency(report.total_spent),
            "average_formatted": _format_currency(report.average_transaction),
            # Sorted categories by amount
            "categories_sorted": sorted(
                report.by_category.items(),
                key=lambda x: float(x[1]["total"]),
                reverse=True,
            ),
            # Sorted merchants by amount
            "merchants_sorted": sorted(
                report.top_merchants,
                key=lambda x: float(x["total"]),
                reverse=True,
            ),
        }

        try:
            return template.render(**context)
        except Exception as e:
            raise ReportGenerationError(
                f"Failed to render Markdown template: {e}",
                template="summary.md.j2",
                format="markdown",
            ) from e

    def get_default_filename(self, format: str = "html") -> str:
        """Generate default filename with current date.

        Args:
            format: Report format - "html" or "markdown".

        Returns:
            Filename like "spending_report_2024_11_15.html"

        Raises:
            ValueError: If format is not "html" or "markdown".
        """
        if format not in ("html", "markdown"):
            raise ValueError(f"Invalid format: {format}. Must be 'html' or 'markdown'.")

        date_str = _format_date_for_filename(date.today())
        extension = "html" if format == "html" else "md"
        return f"spending_report_{date_str}.{extension}"

    def save_report(
        self,
        content: str,
        path: Path,
        overwrite: bool = False,
    ) -> None:
        """Save report content to file.

        Creates parent directories if they don't exist. By default,
        raises error if file already exists to prevent accidental
        overwrites.

        Args:
            content: Report content (HTML or Markdown).
            path: Output file path.
            overwrite: If True, overwrite existing files. Defaults to False.

        Raises:
            FileExistsError: If file exists and overwrite is False.
        """
        if path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {path}. Use overwrite=True to replace.")

        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write content
        path.write_text(content, encoding="utf-8")
