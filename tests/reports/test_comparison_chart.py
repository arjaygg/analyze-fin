"""
Tests for period comparison chart.
"""

import plotly.graph_objects as go

from analyze_fin.reports.charts import ChartBuilder


class TestCreatePeriodComparison:
    """Tests for create_period_comparison method (AC5)."""

    def test_create_period_comparison_returns_figure(self, sample_comparison_data: dict) -> None:
        builder = ChartBuilder()
        fig = builder.create_period_comparison(sample_comparison_data)
        assert isinstance(fig, go.Figure)

    def test_create_period_comparison_has_correct_title(self, sample_comparison_data: dict) -> None:
        builder = ChartBuilder()
        fig = builder.create_period_comparison(sample_comparison_data)
        assert fig.layout.title.text == "Period Comparison"

    def test_create_period_comparison_accepts_custom_title(self, sample_comparison_data: dict) -> None:
        builder = ChartBuilder()
        fig = builder.create_period_comparison(sample_comparison_data, title="Oct vs Nov")
        assert fig.layout.title.text == "Oct vs Nov"

    def test_create_period_comparison_has_two_bars(self, sample_comparison_data: dict) -> None:
        builder = ChartBuilder()
        fig = builder.create_period_comparison(sample_comparison_data)
        assert len(fig.data) == 2

    def test_create_period_comparison_shows_period_labels(self, sample_comparison_data: dict) -> None:
        builder = ChartBuilder()
        fig = builder.create_period_comparison(
            sample_comparison_data,
            period_a_label="October",
            period_b_label="November",
        )
        trace_names = [trace.name for trace in fig.data]
        assert "October" in trace_names
        assert "November" in trace_names

    def test_create_period_comparison_values_match_totals(self, sample_comparison_data: dict) -> None:
        builder = ChartBuilder()
        fig = builder.create_period_comparison(sample_comparison_data)

        period_a_value = fig.data[0].y[0]
        period_b_value = fig.data[1].y[0]
        assert period_a_value == float(sample_comparison_data["period_a_total"])
        assert period_b_value == float(sample_comparison_data["period_b_total"])

    def test_create_period_comparison_uses_different_colors(self, sample_comparison_data: dict) -> None:
        builder = ChartBuilder()
        fig = builder.create_period_comparison(sample_comparison_data)

        assert fig.data[0].marker.color is not None
        assert fig.data[1].marker.color is not None
        assert fig.data[0].marker.color != fig.data[1].marker.color

    def test_create_period_comparison_shows_increase(self, sample_comparison_data: dict) -> None:
        builder = ChartBuilder()
        fig = builder.create_period_comparison(sample_comparison_data)

        assert len(fig.layout.annotations) > 0
        annotation_text = fig.layout.annotations[0].text
        assert "+" in annotation_text or "↑" in annotation_text or "20" in annotation_text

    def test_create_period_comparison_shows_decrease(self, comparison_decrease: dict) -> None:
        builder = ChartBuilder()
        fig = builder.create_period_comparison(comparison_decrease)

        assert len(fig.layout.annotations) > 0
        annotation_text = fig.layout.annotations[0].text
        assert "-" in annotation_text or "↓" in annotation_text or "25" in annotation_text

    def test_create_period_comparison_handles_zero_data(self, empty_comparison: dict) -> None:
        builder = ChartBuilder()
        fig = builder.create_period_comparison(empty_comparison)
        assert isinstance(fig, go.Figure)


