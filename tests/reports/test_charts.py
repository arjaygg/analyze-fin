# tests/reports/test_charts.py
"""Tests for ChartBuilder visualization class.

Test structure follows BDD pattern:
- Given: Setup test data and fixtures
- When: Execute the method under test
- Then: Assert expected outcomes
"""

import plotly.graph_objects as go
import pytest

from analyze_fin.reports.charts import ChartBuilder


class TestChartBuilderInitialization:
    """Tests for ChartBuilder class initialization and configuration."""

    def test_chartbuilder_initializes_with_default_colors(self) -> None:
        """Given no color theme, When ChartBuilder is created, Then default colors are used."""
        builder = ChartBuilder()

        assert builder is not None
        assert hasattr(builder, "colors")
        assert len(builder.colors) > 0

    def test_chartbuilder_accepts_custom_color_theme(self) -> None:
        """Given custom colors, When ChartBuilder is created, Then custom colors are used."""
        custom_colors = ["#FF0000", "#00FF00", "#0000FF"]
        builder = ChartBuilder(colors=custom_colors)

        assert builder.colors == custom_colors

    def test_chartbuilder_default_colors_are_visually_distinct(self) -> None:
        """Given default colors, When colors are retrieved, Then at least 8 distinct colors exist."""
        builder = ChartBuilder()

        # Should have enough colors for typical category count
        assert len(builder.colors) >= 8
        # All colors should be unique
        assert len(set(builder.colors)) == len(builder.colors)


class TestChartBuilderDefaultColors:
    """Tests for the _get_default_colors method."""

    def test_get_default_colors_returns_list(self) -> None:
        """Given ChartBuilder, When _get_default_colors is called, Then list is returned."""
        builder = ChartBuilder()
        colors = builder._get_default_colors()

        assert isinstance(colors, list)
        assert all(isinstance(c, str) for c in colors)

    def test_default_colors_are_valid_hex_or_named(self) -> None:
        """Given default colors, When validated, Then all are valid color formats."""
        builder = ChartBuilder()
        colors = builder._get_default_colors()

        for color in colors:
            # Color should be hex format (#RRGGBB) or named color
            assert color.startswith("#") or color.isalpha() or "rgb" in color.lower()


class TestChartBuilderToHtml:
    """Tests for the to_html method."""

    def test_to_html_converts_figure_to_html_string(self) -> None:
        """Given a Plotly figure, When to_html is called, Then HTML string is returned."""
        builder = ChartBuilder()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=["A", "B"], y=[1, 2]))

        html = builder.to_html(fig)

        assert isinstance(html, str)
        assert len(html) > 0

    def test_to_html_produces_embeddable_html(self) -> None:
        """Given a figure, When to_html is called, Then HTML is embeddable (not full page)."""
        builder = ChartBuilder()
        fig = go.Figure()

        html = builder.to_html(fig)

        # Should contain div for embedding
        assert "<div" in html
        # Should NOT be a full HTML page (no <html> or <body> tags)
        assert "<html>" not in html.lower()
        assert "<body>" not in html.lower()

    def test_to_html_includes_plotly_js_reference(self) -> None:
        """Given a figure, When to_html is called, Then Plotly JS is referenced via CDN."""
        builder = ChartBuilder()
        fig = go.Figure()

        html = builder.to_html(fig)

        # Should reference Plotly JS (either inline or CDN)
        assert "plotly" in html.lower()


# Fixtures for chart tests
@pytest.fixture
def sample_by_category() -> dict[str, dict]:
    """Sample category spending data matching SpendingReport.by_category format."""
    from decimal import Decimal

    return {
        "Food & Dining": {"total": Decimal("15000.00"), "count": 40, "percentage": 30.0},
        "Transportation": {"total": Decimal("8000.00"), "count": 25, "percentage": 16.0},
        "Shopping": {"total": Decimal("12000.00"), "count": 20, "percentage": 24.0},
        "Utilities": {"total": Decimal("5000.00"), "count": 10, "percentage": 10.0},
        "Entertainment": {"total": Decimal("10000.00"), "count": 15, "percentage": 20.0},
    }


@pytest.fixture
def empty_by_category() -> dict[str, dict]:
    """Empty category data."""
    return {}


@pytest.fixture
def single_category() -> dict[str, dict]:
    """Single category data (100% case)."""
    from decimal import Decimal

    return {
        "Food & Dining": {"total": Decimal("50000.00"), "count": 100, "percentage": 100.0},
    }


class TestCreateCategoryPie:
    """Tests for create_category_pie method (AC2)."""

    def test_create_category_pie_returns_figure(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When create_category_pie is called, Then Figure is returned."""
        builder = ChartBuilder()

        fig = builder.create_category_pie(sample_by_category)

        assert isinstance(fig, go.Figure)

    def test_create_category_pie_has_correct_title(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When pie chart is created, Then title is 'Spending by Category'."""
        builder = ChartBuilder()

        fig = builder.create_category_pie(sample_by_category)

        assert fig.layout.title.text == "Spending by Category"

    def test_create_category_pie_accepts_custom_title(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given custom title, When pie chart is created, Then custom title is used."""
        builder = ChartBuilder()

        fig = builder.create_category_pie(sample_by_category, title="My Custom Title")

        assert fig.layout.title.text == "My Custom Title"

    def test_create_category_pie_contains_all_categories(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When pie chart is created, Then all categories are present."""
        builder = ChartBuilder()

        fig = builder.create_category_pie(sample_by_category)

        # Get labels from the pie trace
        pie_trace = fig.data[0]
        labels = list(pie_trace.labels)

        for category in sample_by_category:
            assert category in labels

    def test_create_category_pie_values_match_totals(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When pie chart is created, Then values match category totals."""
        builder = ChartBuilder()

        fig = builder.create_category_pie(sample_by_category)

        pie_trace = fig.data[0]
        values = list(pie_trace.values)
        labels = list(pie_trace.labels)

        for i, label in enumerate(labels):
            expected = float(sample_by_category[label]["total"])
            assert values[i] == expected

    def test_create_category_pie_has_hover_template(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When pie chart is created, Then hover shows details."""
        builder = ChartBuilder()

        fig = builder.create_category_pie(sample_by_category)

        pie_trace = fig.data[0]
        # Should have custom hover template with peso formatting
        assert pie_trace.hovertemplate is not None
        assert "%" in pie_trace.hovertemplate  # Shows percentage

    def test_create_category_pie_uses_distinct_colors(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When pie chart is created, Then colors are applied."""
        builder = ChartBuilder()

        fig = builder.create_category_pie(sample_by_category)

        pie_trace = fig.data[0]
        # Should have colors set (either via marker.colors or colorway)
        assert pie_trace.marker.colors is not None or fig.layout.colorway is not None

    def test_create_category_pie_with_empty_data_returns_none(
        self, empty_by_category: dict[str, dict]
    ) -> None:
        """Given empty data, When pie chart is created, Then None is returned."""
        builder = ChartBuilder()

        result = builder.create_category_pie(empty_by_category)

        assert result is None

    def test_create_category_pie_with_single_category(
        self, single_category: dict[str, dict]
    ) -> None:
        """Given single category (100%), When pie chart is created, Then chart renders."""
        builder = ChartBuilder()

        fig = builder.create_category_pie(single_category)

        assert isinstance(fig, go.Figure)
        pie_trace = fig.data[0]
        assert len(list(pie_trace.labels)) == 1

    def test_create_category_pie_sorts_by_amount_descending(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When pie chart is created, Then largest slice is first."""
        builder = ChartBuilder()

        fig = builder.create_category_pie(sample_by_category)

        pie_trace = fig.data[0]
        values = list(pie_trace.values)

        # First value should be the largest (sorted descending)
        assert values[0] == max(values)


# Fixtures for line chart tests
@pytest.fixture
def sample_by_month() -> dict[str, dict]:
    """Sample monthly spending data matching SpendingReport.by_month format."""
    from decimal import Decimal

    return {
        "2024-09": {"total": Decimal("18000.00"), "count": 35},
        "2024-10": {"total": Decimal("20000.00"), "count": 45},
        "2024-11": {"total": Decimal("30000.00"), "count": 55},
        "2024-12": {"total": Decimal("25000.00"), "count": 50},
    }


@pytest.fixture
def empty_by_month() -> dict[str, dict]:
    """Empty monthly data."""
    return {}


@pytest.fixture
def single_month() -> dict[str, dict]:
    """Single month data point."""
    from decimal import Decimal

    return {
        "2024-11": {"total": Decimal("50000.00"), "count": 100},
    }


class TestCreateSpendingTrend:
    """Tests for create_spending_trend method (AC3)."""

    def test_create_spending_trend_returns_figure(
        self, sample_by_month: dict[str, dict]
    ) -> None:
        """Given monthly data, When create_spending_trend is called, Then Figure is returned."""
        builder = ChartBuilder()

        fig = builder.create_spending_trend(sample_by_month)

        assert isinstance(fig, go.Figure)

    def test_create_spending_trend_has_correct_title(
        self, sample_by_month: dict[str, dict]
    ) -> None:
        """Given monthly data, When line chart is created, Then title is 'Spending Over Time'."""
        builder = ChartBuilder()

        fig = builder.create_spending_trend(sample_by_month)

        assert fig.layout.title.text == "Spending Over Time"

    def test_create_spending_trend_accepts_custom_title(
        self, sample_by_month: dict[str, dict]
    ) -> None:
        """Given custom title, When line chart is created, Then custom title is used."""
        builder = ChartBuilder()

        fig = builder.create_spending_trend(sample_by_month, title="Monthly Trend")

        assert fig.layout.title.text == "Monthly Trend"

    def test_create_spending_trend_has_correct_axes(
        self, sample_by_month: dict[str, dict]
    ) -> None:
        """Given monthly data, When line chart is created, Then axes are properly labeled."""
        builder = ChartBuilder()

        fig = builder.create_spending_trend(sample_by_month)

        # Y-axis should show peso amounts
        assert "₱" in str(fig.layout.yaxis.tickprefix) or fig.layout.yaxis.title.text

    def test_create_spending_trend_contains_all_months(
        self, sample_by_month: dict[str, dict]
    ) -> None:
        """Given monthly data, When line chart is created, Then all months are present."""
        builder = ChartBuilder()

        fig = builder.create_spending_trend(sample_by_month)

        line_trace = fig.data[0]
        x_values = list(line_trace.x)

        assert len(x_values) == len(sample_by_month)

    def test_create_spending_trend_values_match_totals(
        self, sample_by_month: dict[str, dict]
    ) -> None:
        """Given monthly data, When line chart is created, Then values match month totals."""
        builder = ChartBuilder()

        fig = builder.create_spending_trend(sample_by_month)

        line_trace = fig.data[0]
        y_values = list(line_trace.y)

        # Values should be floats from Decimal totals
        expected_values = sorted(
            [float(data["total"]) for data in sample_by_month.values()]
        )
        actual_values = sorted(y_values)
        assert actual_values == expected_values

    def test_create_spending_trend_has_hover_template(
        self, sample_by_month: dict[str, dict]
    ) -> None:
        """Given monthly data, When line chart is created, Then hover shows details with peso symbol."""
        builder = ChartBuilder()

        fig = builder.create_spending_trend(sample_by_month)

        line_trace = fig.data[0]
        # Should have custom hover template with peso formatting
        assert line_trace.hovertemplate is not None
        assert "₱" in line_trace.hovertemplate

    def test_create_spending_trend_with_empty_data_returns_none(
        self, empty_by_month: dict[str, dict]
    ) -> None:
        """Given empty data, When line chart is created, Then None is returned."""
        builder = ChartBuilder()

        result = builder.create_spending_trend(empty_by_month)

        assert result is None

    def test_create_spending_trend_with_single_month(
        self, single_month: dict[str, dict]
    ) -> None:
        """Given single month, When line chart is created, Then chart renders."""
        builder = ChartBuilder()

        fig = builder.create_spending_trend(single_month)

        assert isinstance(fig, go.Figure)
        line_trace = fig.data[0]
        assert len(list(line_trace.x)) == 1

    def test_create_spending_trend_months_sorted_chronologically(
        self, sample_by_month: dict[str, dict]
    ) -> None:
        """Given monthly data, When line chart is created, Then months are sorted."""
        builder = ChartBuilder()

        fig = builder.create_spending_trend(sample_by_month)

        line_trace = fig.data[0]
        x_values = list(line_trace.x)

        # Should be sorted chronologically
        assert x_values == sorted(x_values)


class TestCreateCategoryBar:
    """Tests for create_category_bar method (AC4)."""

    def test_create_category_bar_returns_figure(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When create_category_bar is called, Then Figure is returned."""
        builder = ChartBuilder()

        fig = builder.create_category_bar(sample_by_category)

        assert isinstance(fig, go.Figure)

    def test_create_category_bar_has_correct_title(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When bar chart is created, Then title is correct."""
        builder = ChartBuilder()

        fig = builder.create_category_bar(sample_by_category)

        assert fig.layout.title.text == "Category Spending Comparison"

    def test_create_category_bar_accepts_custom_title(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given custom title, When bar chart is created, Then custom title is used."""
        builder = ChartBuilder()

        fig = builder.create_category_bar(sample_by_category, title="My Bar Chart")

        assert fig.layout.title.text == "My Bar Chart"

    def test_create_category_bar_contains_all_categories(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When bar chart is created, Then all categories are present."""
        builder = ChartBuilder()

        fig = builder.create_category_bar(sample_by_category)

        bar_trace = fig.data[0]
        x_values = list(bar_trace.x)

        assert len(x_values) == len(sample_by_category)
        for category in sample_by_category:
            assert category in x_values

    def test_create_category_bar_sorted_descending(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When bar chart is created, Then bars are sorted descending."""
        builder = ChartBuilder()

        fig = builder.create_category_bar(sample_by_category)

        bar_trace = fig.data[0]
        y_values = list(bar_trace.y)

        # Should be sorted descending (first bar is largest)
        assert y_values == sorted(y_values, reverse=True)

    def test_create_category_bar_has_hover_template(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When bar chart is created, Then hover shows details."""
        builder = ChartBuilder()

        fig = builder.create_category_bar(sample_by_category)

        bar_trace = fig.data[0]
        # Should have custom hover template
        assert bar_trace.hovertemplate is not None
        assert "₱" in bar_trace.hovertemplate

    def test_create_category_bar_with_empty_data_returns_none(
        self, empty_by_category: dict[str, dict]
    ) -> None:
        """Given empty data, When bar chart is created, Then None is returned."""
        builder = ChartBuilder()

        result = builder.create_category_bar(empty_by_category)

        assert result is None

    def test_create_category_bar_uses_colors(
        self, sample_by_category: dict[str, dict]
    ) -> None:
        """Given category data, When bar chart is created, Then colors are applied."""
        builder = ChartBuilder()

        fig = builder.create_category_bar(sample_by_category)

        bar_trace = fig.data[0]
        # Should have colors set
        assert bar_trace.marker.color is not None


# Fixtures for comparison chart tests
@pytest.fixture
def sample_comparison_data() -> dict:
    """Sample comparison data matching SpendingAnalyzer.compare_periods format."""
    from decimal import Decimal

    return {
        "period_a_total": Decimal("25000.00"),
        "period_b_total": Decimal("30000.00"),
        "difference": Decimal("5000.00"),
        "change_percent": 20.0,
        "period_a_transactions": 50,
        "period_b_transactions": 60,
    }


@pytest.fixture
def comparison_decrease() -> dict:
    """Comparison data showing spending decrease."""
    from decimal import Decimal

    return {
        "period_a_total": Decimal("40000.00"),
        "period_b_total": Decimal("30000.00"),
        "difference": Decimal("-10000.00"),
        "change_percent": -25.0,
        "period_a_transactions": 80,
        "period_b_transactions": 60,
    }


@pytest.fixture
def empty_comparison() -> dict:
    """Empty/zero comparison data."""
    from decimal import Decimal

    return {
        "period_a_total": Decimal("0"),
        "period_b_total": Decimal("0"),
        "difference": Decimal("0"),
        "change_percent": 0.0,
        "period_a_transactions": 0,
        "period_b_transactions": 0,
    }


class TestCreatePeriodComparison:
    """Tests for create_period_comparison method (AC5)."""

    def test_create_period_comparison_returns_figure(
        self, sample_comparison_data: dict
    ) -> None:
        """Given comparison data, When create_period_comparison is called, Then Figure is returned."""
        builder = ChartBuilder()

        fig = builder.create_period_comparison(sample_comparison_data)

        assert isinstance(fig, go.Figure)

    def test_create_period_comparison_has_correct_title(
        self, sample_comparison_data: dict
    ) -> None:
        """Given comparison data, When chart is created, Then title is 'Period Comparison'."""
        builder = ChartBuilder()

        fig = builder.create_period_comparison(sample_comparison_data)

        assert fig.layout.title.text == "Period Comparison"

    def test_create_period_comparison_accepts_custom_title(
        self, sample_comparison_data: dict
    ) -> None:
        """Given custom title, When chart is created, Then custom title is used."""
        builder = ChartBuilder()

        fig = builder.create_period_comparison(
            sample_comparison_data, title="Oct vs Nov"
        )

        assert fig.layout.title.text == "Oct vs Nov"

    def test_create_period_comparison_has_two_bars(
        self, sample_comparison_data: dict
    ) -> None:
        """Given comparison data, When chart is created, Then two bars are shown."""
        builder = ChartBuilder()

        fig = builder.create_period_comparison(sample_comparison_data)

        # Should have two traces (one for each period)
        assert len(fig.data) == 2

    def test_create_period_comparison_shows_period_labels(
        self, sample_comparison_data: dict
    ) -> None:
        """Given comparison data, When chart is created, Then periods are labeled."""
        builder = ChartBuilder()

        fig = builder.create_period_comparison(
            sample_comparison_data,
            period_a_label="October",
            period_b_label="November",
        )

        # Check that traces have correct names
        trace_names = [trace.name for trace in fig.data]
        assert "October" in trace_names
        assert "November" in trace_names

    def test_create_period_comparison_values_match_totals(
        self, sample_comparison_data: dict
    ) -> None:
        """Given comparison data, When chart is created, Then values match totals."""
        builder = ChartBuilder()

        fig = builder.create_period_comparison(sample_comparison_data)

        # Get the y values from both traces
        period_a_value = fig.data[0].y[0]
        period_b_value = fig.data[1].y[0]

        assert period_a_value == float(sample_comparison_data["period_a_total"])
        assert period_b_value == float(sample_comparison_data["period_b_total"])

    def test_create_period_comparison_uses_different_colors(
        self, sample_comparison_data: dict
    ) -> None:
        """Given comparison data, When chart is created, Then bars have different colors."""
        builder = ChartBuilder()

        fig = builder.create_period_comparison(sample_comparison_data)

        # Both traces should have colors set
        assert fig.data[0].marker.color is not None
        assert fig.data[1].marker.color is not None
        # Colors should be different
        assert fig.data[0].marker.color != fig.data[1].marker.color

    def test_create_period_comparison_shows_increase(
        self, sample_comparison_data: dict
    ) -> None:
        """Given spending increase, When chart is created, Then annotation shows increase."""
        builder = ChartBuilder()

        fig = builder.create_period_comparison(sample_comparison_data)

        # Should have annotation showing change
        assert len(fig.layout.annotations) > 0
        annotation_text = fig.layout.annotations[0].text
        # Should contain up arrow or positive indicator
        assert "+" in annotation_text or "↑" in annotation_text or "20" in annotation_text

    def test_create_period_comparison_shows_decrease(
        self, comparison_decrease: dict
    ) -> None:
        """Given spending decrease, When chart is created, Then annotation shows decrease."""
        builder = ChartBuilder()

        fig = builder.create_period_comparison(comparison_decrease)

        # Should have annotation showing change
        assert len(fig.layout.annotations) > 0
        annotation_text = fig.layout.annotations[0].text
        # Should contain down arrow or negative indicator
        assert "-" in annotation_text or "↓" in annotation_text or "25" in annotation_text

    def test_create_period_comparison_handles_zero_data(
        self, empty_comparison: dict
    ) -> None:
        """Given zero comparison data, When chart is created, Then chart still renders."""
        builder = ChartBuilder()

        fig = builder.create_period_comparison(empty_comparison)

        # Should still return a figure
        assert isinstance(fig, go.Figure)


# Fixtures for top merchants chart tests
@pytest.fixture
def sample_top_merchants() -> list[dict]:
    """Sample top merchants data matching SpendingReport.top_merchants format."""
    from decimal import Decimal

    return [
        {"merchant": "Jollibee", "total": Decimal("5000.00"), "count": 15},
        {"merchant": "Grab", "total": Decimal("4000.00"), "count": 20},
        {"merchant": "7-Eleven", "total": Decimal("3500.00"), "count": 25},
        {"merchant": "SM Supermarket", "total": Decimal("3000.00"), "count": 8},
        {"merchant": "Shopee", "total": Decimal("2500.00"), "count": 10},
    ]


@pytest.fixture
def empty_merchants() -> list[dict]:
    """Empty merchants list."""
    return []


@pytest.fixture
def many_merchants() -> list[dict]:
    """More than 10 merchants for limit testing."""
    from decimal import Decimal

    return [
        {"merchant": f"Merchant {i}", "total": Decimal(str(1000 * (15 - i))), "count": i + 5}
        for i in range(15)
    ]


class TestCreateTopMerchantsBar:
    """Tests for create_top_merchants_bar method (AC4)."""

    def test_create_top_merchants_bar_returns_figure(
        self, sample_top_merchants: list[dict]
    ) -> None:
        """Given merchants data, When create_top_merchants_bar is called, Then Figure is returned."""
        builder = ChartBuilder()

        fig = builder.create_top_merchants_bar(sample_top_merchants)

        assert isinstance(fig, go.Figure)

    def test_create_top_merchants_bar_has_correct_title(
        self, sample_top_merchants: list[dict]
    ) -> None:
        """Given merchants data, When chart is created, Then title is correct."""
        builder = ChartBuilder()

        fig = builder.create_top_merchants_bar(sample_top_merchants)

        assert fig.layout.title.text == "Top Merchants"

    def test_create_top_merchants_bar_accepts_custom_title(
        self, sample_top_merchants: list[dict]
    ) -> None:
        """Given custom title, When chart is created, Then custom title is used."""
        builder = ChartBuilder()

        fig = builder.create_top_merchants_bar(sample_top_merchants, title="My Top Merchants")

        assert fig.layout.title.text == "My Top Merchants"

    def test_create_top_merchants_bar_is_horizontal(
        self, sample_top_merchants: list[dict]
    ) -> None:
        """Given merchants data, When chart is created, Then bars are horizontal."""
        builder = ChartBuilder()

        fig = builder.create_top_merchants_bar(sample_top_merchants)

        bar_trace = fig.data[0]
        # Horizontal bar has orientation='h'
        assert bar_trace.orientation == "h"

    def test_create_top_merchants_bar_contains_all_merchants(
        self, sample_top_merchants: list[dict]
    ) -> None:
        """Given merchants data, When chart is created, Then all merchants are present."""
        builder = ChartBuilder()

        fig = builder.create_top_merchants_bar(sample_top_merchants)

        bar_trace = fig.data[0]
        y_values = list(bar_trace.y)

        assert len(y_values) == len(sample_top_merchants)
        for merchant in sample_top_merchants:
            assert merchant["merchant"] in y_values

    def test_create_top_merchants_bar_limits_to_max(
        self, many_merchants: list[dict]
    ) -> None:
        """Given >10 merchants, When chart is created with default limit, Then only top 10 shown."""
        builder = ChartBuilder()

        fig = builder.create_top_merchants_bar(many_merchants)

        bar_trace = fig.data[0]
        y_values = list(bar_trace.y)

        assert len(y_values) == 10

    def test_create_top_merchants_bar_custom_limit(
        self, many_merchants: list[dict]
    ) -> None:
        """Given >10 merchants and custom limit, When chart is created, Then limit is respected."""
        builder = ChartBuilder()

        fig = builder.create_top_merchants_bar(many_merchants, max_merchants=5)

        bar_trace = fig.data[0]
        y_values = list(bar_trace.y)

        assert len(y_values) == 5

    def test_create_top_merchants_bar_has_hover_template(
        self, sample_top_merchants: list[dict]
    ) -> None:
        """Given merchants data, When chart is created, Then hover shows details."""
        builder = ChartBuilder()

        fig = builder.create_top_merchants_bar(sample_top_merchants)

        bar_trace = fig.data[0]
        assert bar_trace.hovertemplate is not None
        assert "₱" in bar_trace.hovertemplate

    def test_create_top_merchants_bar_with_empty_data_returns_none(
        self, empty_merchants: list[dict]
    ) -> None:
        """Given empty data, When chart is created, Then None is returned."""
        builder = ChartBuilder()

        result = builder.create_top_merchants_bar(empty_merchants)

        assert result is None

    def test_create_top_merchants_bar_sorted_by_amount(
        self, sample_top_merchants: list[dict]
    ) -> None:
        """Given merchants data, When chart is created, Then largest is at top visually."""
        builder = ChartBuilder()

        fig = builder.create_top_merchants_bar(sample_top_merchants)

        bar_trace = fig.data[0]
        x_values = list(bar_trace.x)
        y_values = list(bar_trace.y)

        # For horizontal bars with largest at top, data is in ascending order
        # (index 0 = bottom of chart = smallest, last index = top = largest)
        # Verify ascending order (smallest to largest)
        for i in range(len(x_values) - 1):
            assert x_values[i] <= x_values[i + 1]

        # Verify the last merchant (top of chart) has the highest value
        expected_max = max(float(m["total"]) for m in sample_top_merchants)
        assert x_values[-1] == expected_max


# Fixtures for integration tests
@pytest.fixture
def sample_spending_report():
    """Complete SpendingReport fixture for integration testing."""
    from decimal import Decimal

    from analyze_fin.analysis.spending import SpendingReport

    return SpendingReport(
        total_spent=Decimal("50000.00"),
        total_transactions=100,
        average_transaction=Decimal("500.00"),
        by_category={
            "Food & Dining": {"total": Decimal("15000.00"), "count": 40, "percentage": 30.0},
            "Transportation": {"total": Decimal("8000.00"), "count": 25, "percentage": 16.0},
            "Shopping": {"total": Decimal("12000.00"), "count": 20, "percentage": 24.0},
            "Utilities": {"total": Decimal("5000.00"), "count": 10, "percentage": 10.0},
            "Entertainment": {"total": Decimal("10000.00"), "count": 15, "percentage": 20.0},
        },
        by_month={
            "2024-09": {"total": Decimal("18000.00"), "count": 35},
            "2024-10": {"total": Decimal("20000.00"), "count": 45},
            "2024-11": {"total": Decimal("30000.00"), "count": 55},
            "2024-12": {"total": Decimal("25000.00"), "count": 50},
        },
        top_merchants=[
            {"merchant": "Jollibee", "total": Decimal("5000.00"), "count": 15},
            {"merchant": "Grab", "total": Decimal("4000.00"), "count": 20},
            {"merchant": "7-Eleven", "total": Decimal("3500.00"), "count": 25},
            {"merchant": "SM Supermarket", "total": Decimal("3000.00"), "count": 8},
            {"merchant": "Shopee", "total": Decimal("2500.00"), "count": 10},
        ],
    )


class TestGenerateAllCharts:
    """Tests for generate_all_charts integration method (AC6)."""

    def test_generate_all_charts_returns_dict(
        self, sample_spending_report
    ) -> None:
        """Given SpendingReport, When generate_all_charts is called, Then dict is returned."""
        builder = ChartBuilder()

        result = builder.generate_all_charts(sample_spending_report)

        assert isinstance(result, dict)

    def test_generate_all_charts_contains_expected_keys(
        self, sample_spending_report
    ) -> None:
        """Given SpendingReport, When generate_all_charts is called, Then expected chart keys exist."""
        builder = ChartBuilder()

        result = builder.generate_all_charts(sample_spending_report)

        expected_keys = ["category_pie", "spending_trend", "category_bar", "top_merchants"]
        for key in expected_keys:
            assert key in result

    def test_generate_all_charts_values_are_html_strings(
        self, sample_spending_report
    ) -> None:
        """Given SpendingReport, When generate_all_charts is called, Then values are HTML strings."""
        builder = ChartBuilder()

        result = builder.generate_all_charts(sample_spending_report)

        for key, html in result.items():
            assert isinstance(html, str)
            assert "<div" in html
            assert "plotly" in html.lower()

    def test_generate_all_charts_handles_empty_report(self) -> None:
        """Given empty SpendingReport, When generate_all_charts is called, Then empty charts handled."""
        from decimal import Decimal

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

        # Should return dict with None or empty values for empty data
        assert isinstance(result, dict)


class TestChartPerformance:
    """Performance tests for chart generation (NFR3: <5 seconds)."""

    def test_chart_generation_performance(self, sample_spending_report) -> None:
        """Given SpendingReport, When all charts generated, Then completes in <5 seconds."""
        import time

        builder = ChartBuilder()

        start_time = time.time()
        result = builder.generate_all_charts(sample_spending_report)
        end_time = time.time()

        elapsed = end_time - start_time
        assert elapsed < 5.0, f"Chart generation took {elapsed:.2f}s, expected <5s"

    def test_individual_chart_performance(self, sample_spending_report) -> None:
        """Given SpendingReport, When individual charts generated, Then each completes in <1 second."""
        import time

        builder = ChartBuilder()

        # Test each chart type
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
        """Given ChartBuilder, When checking for MIN_DATA_POINTS, Then constant exists."""
        from analyze_fin.reports.charts import MIN_DATA_POINTS

        assert isinstance(MIN_DATA_POINTS, int)
        assert MIN_DATA_POINTS >= 1
