# Story 3.4: Visualization with Plotly Charts

Status: review

## Story

As a user,
I want visual charts showing my spending distribution,
so that I can quickly understand patterns without reading tables.

## Acceptance Criteria

1. **AC1: ChartBuilder Class Structure**
   - Given transaction data exists
   - When I implement chart generation
   - Then `src/analyze_fin/reports/charts.py` contains `ChartBuilder` class
   - And ChartBuilder uses Plotly for interactive HTML charts
   - And Charts support: pie, line, bar formats

2. **AC2: Category Breakdown Pie Chart**
   - Given I want a category breakdown pie chart
   - When I generate a pie chart
   - Then Pie chart shows spending by category
   - And Each slice shows: category name, amount, percentage
   - And Colors are distinct and visually appealing
   - And Chart is interactive (hover shows details)
   - And Largest slice is highlighted or labeled prominently

3. **AC3: Spending Over Time Line Chart**
   - Given I want spending over time line chart
   - When I generate a line chart
   - Then X-axis shows dates (daily, weekly, or monthly)
   - And Y-axis shows spending amount in Philippine Peso (₱)
   - And Line shows trend clearly
   - And Hover displays exact date and amount
   - And Multiple lines can be shown for category comparison

4. **AC4: Category Comparison Bar Chart**
   - Given I want category comparison bar chart
   - When I generate a bar chart
   - Then X-axis shows categories
   - And Y-axis shows total spending
   - And Bars are sorted by amount descending
   - And Colors match category theme
   - And Hover shows exact amounts and transaction counts

5. **AC5: Time Period Comparison Bar Chart**
   - Given I want time period comparison bar chart
   - When I generate a comparison bar chart
   - Then Grouped bars show current vs previous period side-by-side
   - And Legend clearly identifies which bar is which period
   - And Visual difference is easy to spot

6. **AC6: Chart Quality and Performance**
   - Given charts are generated
   - When I verify the output
   - Then Charts are fully interactive (zoom, pan, hover)
   - And Charts are responsive (work on different screen sizes)
   - And Chart generation completes in <5 seconds (NFR3)
   - And Charts are embedded in HTML reports seamlessly

7. **AC7: Empty Data Handling**
   - Given empty or insufficient data
   - When I try to generate a chart
   - Then Placeholder message: "Not enough data to generate chart"
   - And Minimum data requirements are communicated
   - And No error is thrown

## Tasks / Subtasks

- [x] Task 1: Create ChartBuilder class foundation (AC: #1)
  - [x] 1.1 Create `src/analyze_fin/reports/charts.py` module with type hints
  - [x] 1.2 Implement `ChartBuilder` class with `__init__` accepting optional color theme
  - [x] 1.3 Add dependency `plotly` via `uv add plotly` (also added numpy for plotly.express)
  - [x] 1.4 Create base method `_get_default_colors()` returning Philippine-themed color palette
  - [x] 1.5 Add method `to_html(fig) -> str` to convert Plotly figure to embeddable HTML
  - [x] 1.6 Write unit tests for ChartBuilder initialization and color theme (8 tests)

- [x] Task 2: Implement pie chart generation (AC: #2)
  - [x] 2.1 Add method `create_category_pie(by_category: dict[str, dict]) -> go.Figure | None`
  - [x] 2.2 Use `plotly.graph_objects.Pie()` for more control over sorting/colors
  - [x] 2.3 Configure hover template showing: category, amount (₱ formatted), percentage
  - [x] 2.4 Set distinct colors using Philippine-themed palette
  - [x] 2.5 Add title: "Spending by Category" (customizable)
  - [x] 2.6 Write unit tests for pie chart with sample data (10 tests)
  - [x] 2.7 Write test for empty data handling (returns None)

- [x] Task 3: Implement line chart generation (AC: #3)
  - [x] 3.1 Add method `create_spending_trend(by_month: dict[str, dict]) -> go.Figure | None`
  - [x] 3.2 Use `plotly.graph_objects.Scatter()` with lines+markers mode
  - [x] 3.3 Configure hover showing: date, amount (₱ formatted)
  - [x] 3.4 Add title: "Spending Over Time" (customizable)
  - [x] 3.5 Format Y-axis with peso symbol and thousands separator
  - [x] 3.6 Data sorted chronologically
  - [x] 3.7 Write unit tests for line chart with sample monthly data (10 tests)
  - [x] 3.8 Write test for single data point (renders correctly)

- [x] Task 4: Implement bar chart generation (AC: #4)
  - [x] 4.1 Add method `create_category_bar(by_category: dict[str, dict]) -> go.Figure | None`
  - [x] 4.2 Use `plotly.graph_objects.Bar()` with customdata for counts
  - [x] 4.3 Sort bars by amount descending
  - [x] 4.4 Configure hover showing: category, amount (₱ formatted), transaction count
  - [x] 4.5 Add title: "Category Spending Comparison" (customizable)
  - [x] 4.6 Write unit tests for bar chart with sample data (8 tests)

- [x] Task 5: Implement comparison bar chart (AC: #5)
  - [x] 5.1 Add method `create_period_comparison(comparison_data: dict[str, Any]) -> go.Figure`
  - [x] 5.2 Create grouped bar chart with Period A and Period B side by side
  - [x] 5.3 Use different colors for each period with clear legend
  - [x] 5.4 Show difference annotation (↑ or ↓ with percentage, color-coded)
  - [x] 5.5 Add title: "Period Comparison" (customizable, with period labels)
  - [x] 5.6 Write unit tests for comparison chart (10 tests)

- [x] Task 6: Add top merchants bar chart (AC: #4)
  - [x] 6.1 Add method `create_top_merchants_bar(top_merchants: list[dict]) -> go.Figure | None`
  - [x] 6.2 Horizontal bar chart with merchants on Y-axis, amounts on X-axis
  - [x] 6.3 Limit to top 10 merchants (configurable via max_merchants param)
  - [x] 6.4 Configure hover showing: merchant name, total spent, transaction count
  - [x] 6.5 Write unit tests for merchants bar chart (10 tests)

- [x] Task 7: Performance and integration (AC: #6, #7)
  - [x] 7.1 Add `generate_all_charts(report: SpendingReport) -> dict[str, str]` returning HTML strings
  - [x] 7.2 Add timing validation - assert chart generation < 5 seconds (verified)
  - [x] 7.3 Implement empty data checks in all chart methods (all return None for empty)
  - [x] 7.4 Add `MIN_DATA_POINTS` constant and validation
  - [x] 7.5 Write integration test with SpendingAnalyzer output (7 tests)
  - [x] 7.6 Run full test suite ensuring no regressions (494 passed)

### Review Follow-ups (AI)

- [x] [AI-Review][HIGH] Task 7.4 incomplete: MIN_DATA_POINTS constant defined but never used for validation [charts.py:23]
- [x] [AI-Review][HIGH] Fix ruff F401: Remove unused `import plotly.express as px` [charts.py:16]
- [x] [AI-Review][MEDIUM] Fix ruff I001: Sort import block [charts.py:14-17]
- [x] [AI-Review][MEDIUM] Fix ruff C408: Replace 23 `dict()` calls with dict literals `{}` [charts.py:multiple]
- [x] [AI-Review][MEDIUM] Inconsistent return type: `create_period_comparison` returns `go.Figure` but other methods return `go.Figure | None` [charts.py:299]
- [x] [AI-Review][LOW] Test inconsistency: Add ₱ verification to `test_create_spending_trend_has_hover_template` [test_charts.py:365-376]
- [x] [AI-Review][MEDIUM] Fix hardcoded colors in `create_period_comparison`: Replace hex values `#DC143C` (Red) and `#2E8B57` (Green) with module constants [charts.py:374-377] ✅ Added COLOR_SPENDING_INCREASE/DECREASE constants
- [x] [AI-Review][MEDIUM] Add "Others" grouping for high cardinality data: Implement `max_slices` limit (default 10-15) in `create_category_pie` and `create_category_bar` to prevent clutter [charts.py] ✅ Added max_slices/max_bars params with MAX_CHART_ITEMS default
- [x] [AI-Review][LOW] Add untracked files to git: `src/analyze_fin/reports/charts.py` and `tests/reports/test_charts.py` ✅ Committed in ab69bcf

### Review Follow-ups (AI) - Code Review 2026-01-02

- [x] [AI-Review][CRITICAL] C1: Commit all untracked implementation files to git - charts.py, test_charts.py have never been committed [project-wide] ✅ Committed in ab69bcf
- [x] [AI-Review][CRITICAL] C2: Sync story Status field with sprint-status.yaml - story shows "in-progress" but sprint-status shows "review" [3-4-visualization-with-plotly-charts.md:3] ✅ Both now in-progress, updating to review

## Dev Notes

### Architecture Requirements

**File Location:** `src/analyze_fin/reports/charts.py`
- Module already exists as `src/analyze_fin/reports/__init__.py` (empty)
- ChartBuilder will be the primary class in this module

**Data Source Integration:**
- ChartBuilder consumes output from `SpendingAnalyzer.analyze()` which returns `SpendingReport`
- SpendingReport provides:
  - `by_category: dict[str, dict[str, Any]]` with keys: total (Decimal), count (int), percentage (float)
  - `by_month: dict[str, dict[str, Any]]` with keys: total (Decimal), count (int), month format "YYYY-MM"
  - `top_merchants: list[dict[str, Any]]` with keys: merchant, total, count
- ChartBuilder also accepts `SpendingAnalyzer.compare_periods()` output for comparison charts

### Technology Stack

**Plotly Usage (project-context.md mandated):**
```python
import plotly.express as px
import plotly.graph_objects as go

# Pie chart example
fig = px.pie(df, values='amount', names='category', title='Spending by Category')

# Line chart example
fig = px.line(df, x='month', y='amount', title='Spending Over Time')

# Bar chart example
fig = px.bar(df, x='category', y='amount', title='Category Comparison')

# Grouped bar for comparison
fig = go.Figure(data=[
    go.Bar(name='Period A', x=categories, y=period_a_values),
    go.Bar(name='Period B', x=categories, y=period_b_values)
])
fig.update_layout(barmode='group')
```

**HTML Export:**
```python
# For embedding in Jinja2 templates
html_str = fig.to_html(full_html=False, include_plotlyjs='cdn')
```

### Coding Standards (from project-context.md)

**Type Hints Required:**
```python
def create_category_pie(
    self,
    by_category: dict[str, dict[str, Any]],
    title: str = "Spending by Category",
) -> go.Figure:
```

**Currency Formatting:**
- Display: `₱{amount:,.2f}` → `₱12,345.67`
- Use Decimal internally, convert to float only for Plotly

**Color Palette:**
Consider Philippine-themed colors or use Plotly's qualitative scales:
```python
import plotly.express as px
colors = px.colors.qualitative.Set2  # or Pastel1, Safe, etc.
```

### Testing Strategy

**Test File:** `tests/reports/test_charts.py`

**Fixtures Needed:**
```python
@pytest.fixture
def sample_spending_report():
    """SpendingReport with realistic test data."""
    return SpendingReport(
        total_spent=Decimal("50000.00"),
        total_transactions=100,
        average_transaction=Decimal("500.00"),
        by_category={
            "Food & Dining": {"total": Decimal("15000"), "count": 40, "percentage": 30.0},
            "Transportation": {"total": Decimal("8000"), "count": 25, "percentage": 16.0},
            # ... more categories
        },
        by_month={
            "2024-10": {"total": Decimal("20000"), "count": 45},
            "2024-11": {"total": Decimal("30000"), "count": 55},
        },
        top_merchants=[
            {"merchant": "Jollibee", "total": Decimal("5000"), "count": 15},
            {"merchant": "Grab", "total": Decimal("4000"), "count": 20},
        ],
    )
```

**Test Assertions:**
- Chart returns valid `go.Figure` object
- Chart has expected title
- Chart data matches input data
- Empty data returns None or raises no exception
- HTML output is valid string containing `<div>` and Plotly scripts

### Performance Requirements (NFR3)

- Dashboard generation including all charts: <5 seconds
- Single chart generation: <1 second
- Test with 500+ transaction dataset to verify

### Edge Cases to Handle

1. **Empty data:** Return None or placeholder figure
2. **Single data point:** Should still render (line becomes dot, bar single bar)
3. **All same category:** Pie chart shows 100% for one slice
4. **Zero spending:** Handle division by zero in percentages
5. **Missing merchant_normalized:** Fall back to description field
6. **Decimal precision:** Ensure no floating point artifacts in display

### Project Structure Notes

- Alignment: Follows `src/analyze_fin/reports/` pattern already established
- Integration point: ChartBuilder output feeds into Story 3.5 ReportGenerator (templates/reports/*.j2)
- No conflicts detected with existing code

### References

- [Source: _bmad-output/epics.md#Story 3.4: Visualization with Plotly Charts]
- [Source: _bmad-output/project-context.md#Technology Stack & Versions]
- [Source: _bmad-output/project-context.md#Python-Specific Rules]
- [Source: src/analyze_fin/analysis/spending.py - SpendingReport dataclass]
- [Plotly Express Documentation: https://plotly.com/python/plotly-express/]

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

- Task 1: plotly.express requires numpy - added via `uv add numpy`

### Completion Notes List

- **Task 1 (2026-01-02):** Created ChartBuilder class foundation
  - Created `src/analyze_fin/reports/charts.py` with ChartBuilder class
  - Philippine-themed color palette with 12 distinct colors
  - `to_html()` method for embeddable HTML output (uses CDN for Plotly JS)
  - 8 unit tests covering initialization, colors, and HTML conversion
  - Dependencies: plotly, numpy added to project

- **Task 2 (2026-01-02):** Implemented pie chart generation
  - `create_category_pie()` method with hover template showing ₱ formatted amounts
  - Sorted by amount descending (largest slice first)
  - Returns None for empty data
  - 10 additional unit tests (total: 18 tests)

- **Task 3 (2026-01-02):** Implemented line chart generation
  - `create_spending_trend()` method with lines+markers mode
  - Y-axis with ₱ prefix and comma formatting
  - Sorted chronologically, handles single data point
  - 10 additional unit tests (total: 28 tests)

- **Task 4 (2026-01-02):** Implemented bar chart generation
  - `create_category_bar()` method with customdata for transaction counts
  - Sorted descending by amount, hover shows ₱ and count
  - 8 additional unit tests (total: 36 tests)

- **Task 5 (2026-01-02):** Implemented comparison bar chart
  - `create_period_comparison()` with grouped bars for two periods
  - Color-coded annotation showing ↑/↓ with percentage change
  - Customizable period labels for flexibility
  - 10 additional unit tests (total: 46 tests)

- **Task 6 (2026-01-02):** Implemented top merchants horizontal bar chart
  - `create_top_merchants_bar()` with horizontal orientation
  - Configurable max_merchants limit (default 10)
  - Dynamic height based on merchant count
  - 10 additional unit tests (total: 56 tests)

- **Review Follow-ups (2026-01-02):** Addressed 6 code review findings
  - ✅ Resolved review finding [HIGH]: Added `_has_sufficient_data()` helper function that uses MIN_DATA_POINTS constant for validation in all chart methods
  - ✅ Resolved review finding [HIGH]: Removed unused `import plotly.express as px`
  - ✅ Resolved review finding [MEDIUM]: Sorted import block (TYPE_CHECKING, Any alphabetically)
  - ✅ Resolved review finding [MEDIUM]: Replaced all 23 `dict()` calls with dict literals `{}`
  - ✅ Resolved review finding [MEDIUM]: Fixed return type of `create_period_comparison` to `go.Figure | None` for consistency
  - ✅ Resolved review finding [LOW]: Added ₱ symbol verification to `test_create_spending_trend_has_hover_template`
  - All 494 tests pass (63 chart tests), ruff check passes

- **Review Follow-ups (2026-01-02):** Added 3 new findings
  - 🔴 Medium: Fix hardcoded colors in `create_period_comparison`
  - 🔴 Medium: Add "Others" grouping for high cardinality data
  - 🔴 Low: Add untracked files to git

### File List

**Created:**
- `src/analyze_fin/reports/charts.py` - ChartBuilder class
- `tests/reports/__init__.py` - Test module init
- `tests/reports/test_charts.py` - Unit tests for ChartBuilder

**Modified:**
- `pyproject.toml` - Added plotly, numpy dependencies
- `uv.lock` - Updated lock file
- `_bmad-output/implementation-artifacts/sprint-status.yaml` - Status: in-progress

## Change Log

- 2026-01-02: Story created with comprehensive context from epics, architecture, and Plotly documentation
- 2026-01-02: Task 1 completed - ChartBuilder foundation with 8 passing tests
- 2026-01-02: Addressed code review findings - 6 items resolved (2 High, 3 Medium, 1 Low)
- 2026-01-02: Code Review (AI) - 3 new action items added to Tasks/Subtasks
- 2026-01-02: Committed all files to git (ab69bcf), added color constants and "Others" grouping - ALL review items complete
