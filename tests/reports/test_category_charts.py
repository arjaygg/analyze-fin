"""
Tests for category-based charts: pie and bar.
"""

import plotly.graph_objects as go

from analyze_fin.reports.charts import ChartBuilder


class TestCreateCategoryPie:
    """Tests for create_category_pie method (AC2)."""

    def test_create_category_pie_returns_figure(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_pie(sample_by_category)
        assert isinstance(fig, go.Figure)

    def test_create_category_pie_has_correct_title(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_pie(sample_by_category)
        assert fig.layout.title.text == "Spending by Category"

    def test_create_category_pie_accepts_custom_title(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_pie(sample_by_category, title="My Custom Title")
        assert fig.layout.title.text == "My Custom Title"

    def test_create_category_pie_contains_all_categories(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_pie(sample_by_category)

        pie_trace = fig.data[0]
        labels = list(pie_trace.labels)
        for category in sample_by_category:
            assert category in labels

    def test_create_category_pie_values_match_totals(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_pie(sample_by_category)

        pie_trace = fig.data[0]
        values = list(pie_trace.values)
        labels = list(pie_trace.labels)

        for i, label in enumerate(labels):
            expected = float(sample_by_category[label]["total"])
            assert values[i] == expected

    def test_create_category_pie_has_hover_template(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_pie(sample_by_category)

        pie_trace = fig.data[0]
        assert pie_trace.hovertemplate is not None
        assert "%" in pie_trace.hovertemplate

    def test_create_category_pie_uses_distinct_colors(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_pie(sample_by_category)

        pie_trace = fig.data[0]
        assert pie_trace.marker.colors is not None or fig.layout.colorway is not None

    def test_create_category_pie_with_empty_data_returns_none(self, empty_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        result = builder.create_category_pie(empty_by_category)
        assert result is None

    def test_create_category_pie_with_single_category(self, single_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_pie(single_category)

        assert isinstance(fig, go.Figure)
        pie_trace = fig.data[0]
        assert len(list(pie_trace.labels)) == 1

    def test_create_category_pie_sorts_by_amount_descending(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_pie(sample_by_category)

        pie_trace = fig.data[0]
        values = list(pie_trace.values)
        assert values[0] == max(values)


class TestCreateCategoryBar:
    """Tests for create_category_bar method (AC4)."""

    def test_create_category_bar_returns_figure(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_bar(sample_by_category)
        assert isinstance(fig, go.Figure)

    def test_create_category_bar_has_correct_title(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_bar(sample_by_category)
        assert fig.layout.title.text == "Category Spending Comparison"

    def test_create_category_bar_accepts_custom_title(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_bar(sample_by_category, title="My Bar Chart")
        assert fig.layout.title.text == "My Bar Chart"

    def test_create_category_bar_contains_all_categories(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_bar(sample_by_category)

        bar_trace = fig.data[0]
        x_values = list(bar_trace.x)

        assert len(x_values) == len(sample_by_category)
        for category in sample_by_category:
            assert category in x_values

    def test_create_category_bar_sorted_descending(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_bar(sample_by_category)

        bar_trace = fig.data[0]
        y_values = list(bar_trace.y)
        assert y_values == sorted(y_values, reverse=True)

    def test_create_category_bar_has_hover_template(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_bar(sample_by_category)

        bar_trace = fig.data[0]
        assert bar_trace.hovertemplate is not None
        assert "₱" in bar_trace.hovertemplate

    def test_create_category_bar_with_empty_data_returns_none(self, empty_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        result = builder.create_category_bar(empty_by_category)
        assert result is None

    def test_create_category_bar_uses_colors(self, sample_by_category: dict[str, dict]) -> None:
        builder = ChartBuilder()
        fig = builder.create_category_bar(sample_by_category)

        bar_trace = fig.data[0]
        assert bar_trace.marker.color is not None


