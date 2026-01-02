# src/analyze_fin/reports/charts.py
"""Chart generation using Plotly for interactive HTML visualizations.

This module provides the ChartBuilder class for creating various chart types
from spending analysis data. All charts are interactive and can be embedded
in HTML reports.

Example:
    builder = ChartBuilder()
    fig = builder.create_category_pie(spending_report.by_category)
    html = builder.to_html(fig)
"""

from typing import TYPE_CHECKING, Any

import plotly.graph_objects as go

if TYPE_CHECKING:
    from analyze_fin.analysis.spending import SpendingReport

# Minimum data points required to generate meaningful charts
MIN_DATA_POINTS = 1


def _has_sufficient_data(data: dict | list) -> bool:
    """Check if data has at least MIN_DATA_POINTS entries.

    Args:
        data: Dictionary or list to check.

    Returns:
        True if data has sufficient entries, False otherwise.
    """
    return len(data) >= MIN_DATA_POINTS


class ChartBuilder:
    """Build interactive Plotly charts from spending analysis data.

    ChartBuilder provides methods to create pie charts, line charts, bar charts,
    and comparison charts from SpendingReport data. All charts are interactive
    with hover details and can be exported to embeddable HTML.

    Attributes:
        colors: List of color values for chart elements.

    Example:
        builder = ChartBuilder()
        fig = builder.create_category_pie(report.by_category)
        html = builder.to_html(fig)
    """

    def __init__(self, colors: list[str] | None = None) -> None:
        """Initialize ChartBuilder with optional custom color theme.

        Args:
            colors: Optional list of color values (hex or named). If None,
                uses a default Philippine-themed color palette.
        """
        self.colors = colors if colors is not None else self._get_default_colors()

    def _get_default_colors(self) -> list[str]:
        """Get default color palette for charts.

        Returns a visually distinct color palette inspired by Philippine themes
        with warm tropical colors and cool ocean tones.

        Returns:
            List of hex color values.
        """
        # Philippine-inspired color palette:
        # - Sunset orange, Ocean blue, Jungle green, Rice gold
        # - Coral pink, Lagoon teal, Mango yellow, Volcanic gray
        # - Sampaguita white (cream), Jeepney red, Banana leaf, Sky blue
        return [
            "#FF6B35",  # Sunset orange
            "#1E90FF",  # Ocean blue
            "#2E8B57",  # Jungle green
            "#DAA520",  # Rice gold
            "#FF7F7F",  # Coral pink
            "#20B2AA",  # Lagoon teal
            "#FFD700",  # Mango yellow
            "#708090",  # Volcanic gray
            "#F5DEB3",  # Sampaguita cream
            "#DC143C",  # Jeepney red
            "#32CD32",  # Banana leaf
            "#87CEEB",  # Sky blue
        ]

    def to_html(self, fig: go.Figure) -> str:
        """Convert a Plotly figure to embeddable HTML string.

        Generates HTML that can be embedded in Jinja2 templates without
        needing a full HTML page structure. Uses CDN for Plotly JS to
        minimize output size.

        Args:
            fig: Plotly figure to convert.

        Returns:
            HTML string suitable for embedding in templates.
        """
        return fig.to_html(full_html=False, include_plotlyjs="cdn")

    def create_category_pie(
        self,
        by_category: dict[str, dict[str, Any]],
        title: str = "Spending by Category",
    ) -> go.Figure | None:
        """Create a pie chart showing spending distribution by category.

        Generates an interactive pie chart with hover details showing category
        name, amount in Philippine Peso, and percentage of total spending.
        Categories are sorted by amount descending so the largest slice appears
        first.

        Args:
            by_category: Dictionary from SpendingReport.by_category with format:
                {"Category Name": {"total": Decimal, "count": int, "percentage": float}}
            title: Chart title. Defaults to "Spending by Category".

        Returns:
            Plotly Figure object, or None if by_category is empty.

        Example:
            fig = builder.create_category_pie(report.by_category)
            if fig:
                html = builder.to_html(fig)
        """
        if not _has_sufficient_data(by_category):
            return None

        # Sort categories by total amount descending (largest first)
        sorted_categories = sorted(
            by_category.items(),
            key=lambda x: float(x[1]["total"]),
            reverse=True,
        )

        categories = [cat for cat, _ in sorted_categories]
        values = [float(data["total"]) for _, data in sorted_categories]

        # Create pie chart using graph_objects for more control
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=categories,
                    values=values,
                    marker={"colors": self.colors[: len(categories)]},
                    hovertemplate=(
                        "<b>%{label}</b><br>"
                        "Amount: ₱%{value:,.2f}<br>"
                        "Percentage: %{percent}<extra></extra>"
                    ),
                    textinfo="label+percent",
                    textposition="auto",
                    sort=False,  # We already sorted, keep our order
                )
            ]
        )

        fig.update_layout(
            title={"text": title},
            showlegend=True,
            legend={"orientation": "v", "yanchor": "middle", "y": 0.5},
        )

        return fig

    def create_spending_trend(
        self,
        by_month: dict[str, dict[str, Any]],
        title: str = "Spending Over Time",
    ) -> go.Figure | None:
        """Create a line chart showing spending trend over time.

        Generates an interactive line chart with hover details showing date
        and amount in Philippine Peso. Data is sorted chronologically by month.

        Args:
            by_month: Dictionary from SpendingReport.by_month with format:
                {"YYYY-MM": {"total": Decimal, "count": int}}
            title: Chart title. Defaults to "Spending Over Time".

        Returns:
            Plotly Figure object, or None if by_month is empty.

        Example:
            fig = builder.create_spending_trend(report.by_month)
            if fig:
                html = builder.to_html(fig)
        """
        if not _has_sufficient_data(by_month):
            return None

        # Sort months chronologically
        sorted_months = sorted(by_month.items(), key=lambda x: x[0])

        months = [month for month, _ in sorted_months]
        values = [float(data["total"]) for _, data in sorted_months]

        # Create line chart using graph_objects
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=months,
                    y=values,
                    mode="lines+markers",
                    line={"color": self.colors[0], "width": 3},
                    marker={"size": 8, "color": self.colors[0]},
                    hovertemplate=(
                        "<b>%{x}</b><br>" "Amount: ₱%{y:,.2f}<extra></extra>"
                    ),
                )
            ]
        )

        fig.update_layout(
            title={"text": title},
            xaxis={
                "title": "Month",
                "tickangle": -45,
            },
            yaxis={
                "title": "Amount (₱)",
                "tickprefix": "₱",
                "tickformat": ",",
            },
            hovermode="x unified",
        )

        return fig

    def create_category_bar(
        self,
        by_category: dict[str, dict[str, Any]],
        title: str = "Category Spending Comparison",
    ) -> go.Figure | None:
        """Create a bar chart comparing spending across categories.

        Generates an interactive bar chart with hover details showing category
        name, amount in Philippine Peso, and transaction count. Categories are
        sorted by amount descending (highest spending first).

        Args:
            by_category: Dictionary from SpendingReport.by_category with format:
                {"Category Name": {"total": Decimal, "count": int, "percentage": float}}
            title: Chart title. Defaults to "Category Spending Comparison".

        Returns:
            Plotly Figure object, or None if by_category is empty.

        Example:
            fig = builder.create_category_bar(report.by_category)
            if fig:
                html = builder.to_html(fig)
        """
        if not _has_sufficient_data(by_category):
            return None

        # Sort categories by total amount descending
        sorted_categories = sorted(
            by_category.items(),
            key=lambda x: float(x[1]["total"]),
            reverse=True,
        )

        categories = [cat for cat, _ in sorted_categories]
        values = [float(data["total"]) for _, data in sorted_categories]
        counts = [data["count"] for _, data in sorted_categories]

        # Create bar chart
        fig = go.Figure(
            data=[
                go.Bar(
                    x=categories,
                    y=values,
                    marker={"color": self.colors[: len(categories)]},
                    customdata=counts,
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        "Amount: ₱%{y:,.2f}<br>"
                        "Transactions: %{customdata}<extra></extra>"
                    ),
                )
            ]
        )

        fig.update_layout(
            title={"text": title},
            xaxis={
                "title": "Category",
                "tickangle": -45,
            },
            yaxis={
                "title": "Amount (₱)",
                "tickprefix": "₱",
                "tickformat": ",",
            },
        )

        return fig

    def create_period_comparison(
        self,
        comparison_data: dict[str, Any],
        title: str = "Period Comparison",
        period_a_label: str = "Previous Period",
        period_b_label: str = "Current Period",
    ) -> go.Figure | None:
        """Create a grouped bar chart comparing spending between two periods.

        Generates an interactive grouped bar chart showing period A and period B
        side by side, with an annotation showing the change percentage.

        Args:
            comparison_data: Dictionary from SpendingAnalyzer.compare_periods with:
                {"period_a_total": Decimal, "period_b_total": Decimal,
                 "difference": Decimal, "change_percent": float,
                 "period_a_transactions": int, "period_b_transactions": int}
            title: Chart title. Defaults to "Period Comparison".
            period_a_label: Label for first period. Defaults to "Previous Period".
            period_b_label: Label for second period. Defaults to "Current Period".

        Returns:
            Plotly Figure object, or None if comparison_data is empty.

        Example:
            comparison = analyzer.compare_periods(transactions, ...)
            fig = builder.create_period_comparison(comparison)
        """
        if not comparison_data:
            return None

        period_a_total = float(comparison_data["period_a_total"])
        period_b_total = float(comparison_data["period_b_total"])
        change_percent = comparison_data["change_percent"]
        period_a_count = comparison_data["period_a_transactions"]
        period_b_count = comparison_data["period_b_transactions"]

        # Create grouped bar chart
        fig = go.Figure(
            data=[
                go.Bar(
                    name=period_a_label,
                    x=["Total Spending"],
                    y=[period_a_total],
                    marker={"color": self.colors[0]},
                    customdata=[period_a_count],
                    hovertemplate=(
                        f"<b>{period_a_label}</b><br>"
                        "Amount: ₱%{y:,.2f}<br>"
                        "Transactions: %{customdata}<extra></extra>"
                    ),
                ),
                go.Bar(
                    name=period_b_label,
                    x=["Total Spending"],
                    y=[period_b_total],
                    marker={"color": self.colors[1]},
                    customdata=[period_b_count],
                    hovertemplate=(
                        f"<b>{period_b_label}</b><br>"
                        "Amount: ₱%{y:,.2f}<br>"
                        "Transactions: %{customdata}<extra></extra>"
                    ),
                ),
            ]
        )

        # Build change annotation
        if change_percent >= 0:
            change_text = f"↑ +{change_percent:.1f}%"
            change_color = "#DC143C"  # Red for increase (spending more)
        else:
            change_text = f"↓ {change_percent:.1f}%"
            change_color = "#2E8B57"  # Green for decrease (spending less)

        fig.update_layout(
            title={"text": title},
            barmode="group",
            yaxis={
                "title": "Amount (₱)",
                "tickprefix": "₱",
                "tickformat": ",",
            },
            showlegend=True,
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "center", "x": 0.5},
            annotations=[
                {
                    "x": 0.5,
                    "y": max(period_a_total, period_b_total) * 1.1,
                    "xref": "paper",
                    "yref": "y",
                    "text": change_text,
                    "showarrow": False,
                    "font": {"size": 16, "color": change_color, "weight": "bold"},
                }
            ],
        )

        return fig

    def create_top_merchants_bar(
        self,
        top_merchants: list[dict[str, Any]],
        title: str = "Top Merchants",
        max_merchants: int = 10,
    ) -> go.Figure | None:
        """Create a horizontal bar chart showing top merchants by spending.

        Generates an interactive horizontal bar chart with merchants on the
        Y-axis and amounts on the X-axis. Limits display to top N merchants
        sorted by amount descending.

        Args:
            top_merchants: List from SpendingReport.top_merchants with format:
                [{"merchant": str, "total": Decimal, "count": int}, ...]
            title: Chart title. Defaults to "Top Merchants".
            max_merchants: Maximum number of merchants to show. Defaults to 10.

        Returns:
            Plotly Figure object, or None if top_merchants is empty.

        Example:
            fig = builder.create_top_merchants_bar(report.top_merchants)
            if fig:
                html = builder.to_html(fig)
        """
        if not _has_sufficient_data(top_merchants):
            return None

        # Sort by total descending and limit
        sorted_merchants = sorted(
            top_merchants,
            key=lambda x: float(x["total"]),
            reverse=True,
        )[:max_merchants]

        # Reverse for horizontal bar so largest is at top
        sorted_merchants = list(reversed(sorted_merchants))

        merchants = [m["merchant"] for m in sorted_merchants]
        values = [float(m["total"]) for m in sorted_merchants]
        counts = [m["count"] for m in sorted_merchants]

        # Create horizontal bar chart
        fig = go.Figure(
            data=[
                go.Bar(
                    x=values,
                    y=merchants,
                    orientation="h",
                    marker={"color": self.colors[0]},
                    customdata=counts,
                    hovertemplate=(
                        "<b>%{y}</b><br>"
                        "Amount: ₱%{x:,.2f}<br>"
                        "Transactions: %{customdata}<extra></extra>"
                    ),
                )
            ]
        )

        fig.update_layout(
            title={"text": title},
            xaxis={
                "title": "Amount (₱)",
                "tickprefix": "₱",
                "tickformat": ",",
            },
            yaxis={
                "title": "Merchant",
            },
            height=max(400, len(merchants) * 40),  # Dynamic height based on merchant count
        )

        return fig

    def generate_all_charts(
        self,
        report: "SpendingReport",
    ) -> dict[str, str]:
        """Generate all available charts from a SpendingReport.

        Creates pie chart, line chart, category bar chart, and top merchants
        chart from the provided SpendingReport. Each chart is converted to
        embeddable HTML.

        Args:
            report: SpendingReport from SpendingAnalyzer.analyze()

        Returns:
            Dictionary with chart names as keys and HTML strings as values.
            Keys: "category_pie", "spending_trend", "category_bar", "top_merchants"
            Values may be empty string if data is insufficient for that chart.

        Example:
            charts = builder.generate_all_charts(report)
            html_pie = charts["category_pie"]
        """
        result: dict[str, str] = {}

        # Category pie chart
        pie_fig = self.create_category_pie(report.by_category)
        result["category_pie"] = self.to_html(pie_fig) if pie_fig else ""

        # Spending trend line chart
        trend_fig = self.create_spending_trend(report.by_month)
        result["spending_trend"] = self.to_html(trend_fig) if trend_fig else ""

        # Category bar chart
        bar_fig = self.create_category_bar(report.by_category)
        result["category_bar"] = self.to_html(bar_fig) if bar_fig else ""

        # Top merchants chart
        merchants_fig = self.create_top_merchants_bar(report.top_merchants)
        result["top_merchants"] = self.to_html(merchants_fig) if merchants_fig else ""

        return result
