"""
Integration and misc tests for ChartBuilder.
"""

from decimal import Decimal

from analyze_fin.reports.charts import ChartBuilder


class TestGenerateAllCharts:
    """Tests for generate_all_charts integration method (AC6)."""

    def test_generate_all_charts_returns_dict(self, sample_spending_report) -> None:
        builder = ChartBuilder()
        result = builder.generate_all_charts(sample_spending_report)
        assert isinstance(result, dict)

    def test_generate_all_charts_contains_expected_keys(self, sample_spending_report) -> None:
        builder = ChartBuilder()
        result = builder.generate_all_charts(sample_spending_report)

        expected_keys = ["category_pie", "spending_trend", "category_bar", "top_merchants"]
        for key in expected_keys:
            assert key in result

    def test_generate_all_charts_values_are_html_strings(self, sample_spending_report) -> None:
        builder = ChartBuilder()
        result = builder.generate_all_charts(sample_spending_report)

        for _key, html in result.items():
            assert isinstance(html, str)
            assert "<div" in html
            assert "plotly" in html.lower()

    def test_generate_all_charts_handles_empty_report(self) -> None:
        from analyze_fin.analysis.spending import SpendingReport

        empty_report = SpendingReport(
            total_spent=Decimal("0"),
            total_transactions=0,
            average_transaction=Decimal("0"),
            by_category={},
            by_month={},
            top_merchants=[],
        )

        builder = ChartBuilder()
        result = builder.generate_all_charts(empty_report)
        assert isinstance(result, dict)


class TestChartPerformance:
    """Performance tests for chart generation (NFR3: <5 seconds)."""

    def test_chart_generation_performance(self, sample_spending_report) -> None:
        import time

        builder = ChartBuilder()
        start_time = time.time()
        builder.generate_all_charts(sample_spending_report)
        elapsed = time.time() - start_time
        assert elapsed < 5.0, f"Chart generation took {elapsed:.2f}s, expected <5s"

    def test_individual_chart_performance(self, sample_spending_report) -> None:
        import time

        builder = ChartBuilder()

        start = time.time()
        builder.create_category_pie(sample_spending_report.by_category)
        pie_time = time.time() - start
        assert pie_time < 1.0, f"Pie chart took {pie_time:.2f}s"

        start = time.time()
        builder.create_spending_trend(sample_spending_report.by_month)
        line_time = time.time() - start
        assert line_time < 1.0, f"Line chart took {line_time:.2f}s"

        start = time.time()
        builder.create_category_bar(sample_spending_report.by_category)
        bar_time = time.time() - start
        assert bar_time < 1.0, f"Bar chart took {bar_time:.2f}s"

        start = time.time()
        builder.create_top_merchants_bar(sample_spending_report.top_merchants)
        merchants_time = time.time() - start
        assert merchants_time < 1.0, f"Merchants chart took {merchants_time:.2f}s"


class TestMinDataPointsConstant:
    """Tests for MIN_DATA_POINTS constant and validation (AC7)."""

    def test_min_data_points_constant_exists(self) -> None:
        from analyze_fin.reports.charts import MIN_DATA_POINTS

        assert isinstance(MIN_DATA_POINTS, int)
        assert MIN_DATA_POINTS >= 1


