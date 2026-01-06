"""
Tests for ChartBuilder initialization/config and basic HTML rendering.
"""

import plotly.graph_objects as go

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

        assert len(builder.colors) >= 8
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

        assert "<div" in html
        assert "<html>" not in html.lower()
        assert "<body>" not in html.lower()

    def test_to_html_includes_plotly_js_reference(self) -> None:
        """Given a figure, When to_html is called, Then Plotly JS is referenced via CDN."""
        builder = ChartBuilder()
        fig = go.Figure()

        html = builder.to_html(fig)

        assert "plotly" in html.lower()


