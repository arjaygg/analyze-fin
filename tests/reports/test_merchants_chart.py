"""
Tests for top merchants bar chart.
"""

import plotly.graph_objects as go

from analyze_fin.reports.charts import ChartBuilder


class TestCreateTopMerchantsBar:
    """Tests for create_top_merchants_bar method (AC4)."""

    def test_create_top_merchants_bar_returns_figure(self, sample_top_merchants: list[dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_top_merchants_bar(sample_top_merchants)
        assert isinstance(fig, go.Figure)

    def test_create_top_merchants_bar_has_correct_title(self, sample_top_merchants: list[dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_top_merchants_bar(sample_top_merchants)
        assert fig.layout.title.text == "Top Merchants"

    def test_create_top_merchants_bar_accepts_custom_title(self, sample_top_merchants: list[dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_top_merchants_bar(sample_top_merchants, title="My Top Merchants")
        assert fig.layout.title.text == "My Top Merchants"

    def test_create_top_merchants_bar_is_horizontal(self, sample_top_merchants: list[dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_top_merchants_bar(sample_top_merchants)

        bar_trace = fig.data[0]
        assert bar_trace.orientation == "h"

    def test_create_top_merchants_bar_contains_all_merchants(self, sample_top_merchants: list[dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_top_merchants_bar(sample_top_merchants)

        bar_trace = fig.data[0]
        y_values = list(bar_trace.y)

        assert len(y_values) == len(sample_top_merchants)
        for merchant in sample_top_merchants:
            assert merchant["merchant"] in y_values

    def test_create_top_merchants_bar_limits_to_max(self, many_merchants: list[dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_top_merchants_bar(many_merchants)

        bar_trace = fig.data[0]
        y_values = list(bar_trace.y)
        assert len(y_values) == 10

    def test_create_top_merchants_bar_custom_limit(self, many_merchants: list[dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_top_merchants_bar(many_merchants, max_merchants=5)

        bar_trace = fig.data[0]
        y_values = list(bar_trace.y)
        assert len(y_values) == 5

    def test_create_top_merchants_bar_has_hover_template(self, sample_top_merchants: list[dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_top_merchants_bar(sample_top_merchants)

        bar_trace = fig.data[0]
        assert bar_trace.hovertemplate is not None
        assert "₱" in bar_trace.hovertemplate

    def test_create_top_merchants_bar_with_empty_data_returns_none(self, empty_merchants: list[dict]) -> None:
        builder = ChartBuilder()
        result = builder.create_top_merchants_bar(empty_merchants)
        assert result is None

    def test_create_top_merchants_bar_sorted_by_amount(self, sample_top_merchants: list[dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_top_merchants_bar(sample_top_merchants)

        bar_trace = fig.data[0]
        x_values = list(bar_trace.x)

        for i in range(len(x_values) - 1):
            assert x_values[i] <= x_values[i + 1]

        expected_max = max(float(m["total"]) for m in sample_top_merchants)
        assert x_values[-1] == expected_max


