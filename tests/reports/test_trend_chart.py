"""
Tests for the spending trend (line) chart.
"""

import plotly.graph_objects as go

from analyze_fin.reports.charts import ChartBuilder


class TestCreateSpendingTrend:
    """Tests for create_spending_trend method (AC3)."""

    def test_create_spending_trend_returns_figure(self, sample_by_month: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_spending_trend(sample_by_month)
        assert isinstance(fig, go.Figure)

    def test_create_spending_trend_has_correct_title(self, sample_by_month: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_spending_trend(sample_by_month)
        assert fig.layout.title.text == "Spending Over Time"

    def test_create_spending_trend_accepts_custom_title(self, sample_by_month: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_spending_trend(sample_by_month, title="Monthly Trend")
        assert fig.layout.title.text == "Monthly Trend"

    def test_create_spending_trend_has_correct_axes(self, sample_by_month: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_spending_trend(sample_by_month)
        assert "₱" in str(fig.layout.yaxis.tickprefix) or fig.layout.yaxis.title.text

    def test_create_spending_trend_contains_all_months(self, sample_by_month: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_spending_trend(sample_by_month)

        line_trace = fig.data[0]
        x_values = list(line_trace.x)
        assert len(x_values) == len(sample_by_month)

    def test_create_spending_trend_values_match_totals(self, sample_by_month: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_spending_trend(sample_by_month)

        line_trace = fig.data[0]
        y_values = list(line_trace.y)

        expected_values = sorted([float(data["total"]) for data in sample_by_month.values()])
        actual_values = sorted(y_values)
        assert actual_values == expected_values

    def test_create_spending_trend_has_hover_template(self, sample_by_month: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_spending_trend(sample_by_month)

        line_trace = fig.data[0]
        assert line_trace.hovertemplate is not None
        assert "₱" in line_trace.hovertemplate

    def test_create_spending_trend_with_empty_data_returns_none(self, empty_by_month: dict[str, dict]) -> None:
        builder = ChartBuilder()
        result = builder.create_spending_trend(empty_by_month)
        assert result is None

    def test_create_spending_trend_with_single_month(self, single_month: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_spending_trend(single_month)

        assert isinstance(fig, go.Figure)
        line_trace = fig.data[0]
        assert len(list(line_trace.x)) == 1

    def test_create_spending_trend_months_sorted_chronologically(self, sample_by_month: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_spending_trend(sample_by_month)

        line_trace = fig.data[0]
        x_values = list(line_trace.x)
        assert x_values == sorted(x_values)


