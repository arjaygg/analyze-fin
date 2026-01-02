"""Report generation with Plotly charts and Jinja2 templates.

Provides:
- ChartBuilder: Create interactive Plotly charts
- ReportGenerator: Generate HTML and Markdown reports

Example:
    from analyze_fin.reports import ChartBuilder, ReportGenerator
    from analyze_fin.analysis.spending import SpendingAnalyzer

    analyzer = SpendingAnalyzer()
    report = analyzer.analyze(transactions)

    generator = ReportGenerator()
    html = generator.generate_html(report, title="November Report")
    generator.save_report(html, Path("report.html"))
"""

from analyze_fin.reports.charts import ChartBuilder
from analyze_fin.reports.generator import ReportGenerator

__all__ = ["ChartBuilder", "ReportGenerator"]
