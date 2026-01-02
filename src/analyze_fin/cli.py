"""
Command-line interface for analyze-fin.

Main entry point for all CLI commands using Typer framework.

Commands:
- query: Query transactions by category, merchant, date, amount
- parse: Parse bank statement PDFs
- export: Export transactions to CSV/JSON
- categorize: Manually categorize transactions
- report: Generate spending reports
"""

import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

import typer
from rich.console import Console
from rich.table import Table

# Typer app instance
app = typer.Typer(
    name="analyze-fin",
    help="Philippine Personal Finance Tracker - Analyze bank statements and spending",
    no_args_is_help=True,
)

# Rich console for pretty output
console = Console()


# Valid output formats for query command
VALID_FORMATS = ("pretty", "json", "csv")


def _parse_date_range(date_range: str) -> tuple[datetime | None, datetime | None]:
    """Parse date range string into start and end dates.

    Supports formats:
    - "2024-11-01 to 2024-11-30"
    - "November 2024" (whole month)
    - "2024-11" (whole month)

    Returns:
        Tuple of (start_date, end_date)
    """
    import calendar
    import re

    date_range = date_range.strip()

    # Format: "2024-11-01 to 2024-11-30"
    if " to " in date_range:
        parts = date_range.split(" to ")
        start = datetime.strptime(parts[0].strip(), "%Y-%m-%d")
        end = datetime.strptime(parts[1].strip(), "%Y-%m-%d")
        return start, end

    # Format: "November 2024" or "Nov 2024"
    month_year_pattern = r"^([A-Za-z]+)\s+(\d{4})$"
    match = re.match(month_year_pattern, date_range)
    if match:
        month_name, year = match.groups()
        # Parse month name
        for i, name in enumerate(calendar.month_name):
            if name.lower().startswith(month_name.lower()):
                month = i
                break
        else:
            for i, name in enumerate(calendar.month_abbr):
                if name.lower() == month_name.lower():
                    month = i
                    break
            else:
                raise ValueError(f"Unknown month: {month_name}")

        year = int(year)
        start = datetime(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end = datetime(year, month, last_day)
        return start, end

    # Format: "2024-11" (whole month)
    if re.match(r"^\d{4}-\d{2}$", date_range):
        year, month = map(int, date_range.split("-"))
        start = datetime(year, month, 1)
        _, last_day = calendar.monthrange(year, month)
        end = datetime(year, month, last_day)
        return start, end

    raise ValueError(f"Unrecognized date range format: {date_range}")


@app.command()
def query(
    category: str | None = typer.Option(
        None,
        "--category",
        "-c",
        help="Filter by category (e.g., 'Food & Dining')"
    ),
    merchant: str | None = typer.Option(
        None,
        "--merchant",
        "-m",
        help="Filter by merchant name"
    ),
    date_range: str | None = typer.Option(
        None,
        "--date-range",
        "-d",
        help="Filter by date range (e.g., '2024-11-01 to 2024-11-30' or 'November 2024')"
    ),
    amount_min: str | None = typer.Option(
        None,
        "--amount-min",
        help="Minimum transaction amount (e.g., '100.00')"
    ),
    amount_max: str | None = typer.Option(
        None,
        "--amount-max",
        help="Maximum transaction amount (e.g., '5000.00')"
    ),
    output_format: str = typer.Option(
        "pretty",
        "--format",
        "-f",
        help="Output format: pretty, json, csv"
    ),
) -> None:
    """
    Query transactions by category, merchant, date range, or amount.

    Examples:
        # Query by category
        analyze-fin query --category "Food & Dining"

        # Query by date range
        analyze-fin query --date-range "November 2024"

        # Combine filters
        analyze-fin query --category "Food & Dining" --amount-min 500

        # JSON output for scripting
        analyze-fin query --category "Food & Dining" --format json
    """
    from sqlalchemy.orm import Session

    from analyze_fin.database.session import init_db
    from analyze_fin.queries.spending import SpendingQuery

    # Validate output format
    if output_format not in VALID_FORMATS:
        console.print(f"[red]Error:[/red] Invalid format '{output_format}'")
        console.print(f"[dim]Valid formats: {', '.join(VALID_FORMATS)}[/dim]")
        raise typer.Exit(code=2)

    # Parse amount filters to Decimal
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None

    if amount_min:
        try:
            min_amount = Decimal(amount_min)
        except InvalidOperation:
            console.print(f"[red]Error:[/red] Invalid amount-min: '{amount_min}'")
            console.print("[dim]Use numeric format, e.g., '100.00'[/dim]")
            raise typer.Exit(code=2) from None

    if amount_max:
        try:
            max_amount = Decimal(amount_max)
        except InvalidOperation:
            console.print(f"[red]Error:[/red] Invalid amount-max: '{amount_max}'")
            console.print("[dim]Use numeric format, e.g., '5000.00'[/dim]")
            raise typer.Exit(code=2) from None

    # Parse date range
    start_date: datetime | None = None
    end_date: datetime | None = None

    if date_range:
        try:
            start_date, end_date = _parse_date_range(date_range)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            console.print("[dim]Use format: '2024-11-01 to 2024-11-30' or 'November 2024'[/dim]")
            raise typer.Exit(code=2) from None

    # Initialize database and run query
    try:
        engine = init_db()
        with Session(engine) as session:
            query_builder = SpendingQuery(session)

            # Apply filters
            if category:
                query_builder = query_builder.filter_by_category(category)
            if merchant:
                query_builder = query_builder.filter_by_merchant(merchant)
            if start_date or end_date:
                query_builder = query_builder.filter_by_date_range(start_date, end_date)
            if min_amount is not None or max_amount is not None:
                query_builder = query_builder.filter_by_amount(min_amount, max_amount)

            # Execute query
            transactions = query_builder.execute()
            total = query_builder.total_amount()
            count = len(transactions)

            # Output results based on format
            if output_format == "json":
                _output_json(transactions, count, total)
            elif output_format == "csv":
                _output_csv(transactions)
            else:
                _output_pretty(transactions, count, total, category, merchant, date_range)

    except Exception as e:
        console.print(f"[red]Error querying database:[/red] {e}")
        raise typer.Exit(code=1) from None


def _output_pretty(
    transactions: list,
    count: int,
    total: Decimal,
    category: str | None,
    merchant: str | None,
    date_range: str | None,
) -> None:
    """Output transactions in pretty table format."""
    if not transactions:
        console.print("[yellow]No transactions found matching filters.[/yellow]")
        return

    # Create table
    table = Table(title="Transactions")
    table.add_column("Date", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Amount", justify="right", style="green")
    table.add_column("Category", style="magenta")

    for txn in transactions[:50]:  # Limit to 50 for readability
        table.add_row(
            txn.date.strftime("%Y-%m-%d"),
            txn.description[:40] + "..." if len(txn.description) > 40 else txn.description,
            f"₱{txn.amount:,.2f}",
            txn.category or "-",
        )

    console.print(table)
    console.print()
    console.print(f"[bold]Total:[/bold] {count} transactions, ₱{total:,.2f}")

    if count > 50:
        console.print(f"[dim](Showing first 50 of {count} transactions)[/dim]")


def _output_json(transactions: list, count: int, total: Decimal) -> None:
    """Output transactions in JSON format."""
    data = {
        "count": count,
        "total_amount": str(total),
        "transactions": [
            {
                "id": txn.id,
                "date": txn.date.strftime("%Y-%m-%d"),
                "description": txn.description,
                "amount": str(txn.amount),
                "category": txn.category,
                "merchant_normalized": txn.merchant_normalized,
            }
            for txn in transactions
        ],
    }
    console.print(json.dumps(data, indent=2))


def _output_csv(transactions: list) -> None:
    """Output transactions in CSV format."""
    import csv
    import sys

    writer = csv.writer(sys.stdout)
    writer.writerow(["date", "description", "amount", "category", "merchant_normalized"])
    for txn in transactions:
        writer.writerow([
            txn.date.strftime("%Y-%m-%d"),
            txn.description,
            str(txn.amount),
            txn.category or "",
            txn.merchant_normalized or "",
        ])


@app.command()
def parse(
    pdf_paths: list[str] = typer.Argument(
        ...,
        help="Path(s) to PDF bank statement files"
    ),
    password: str | None = typer.Option(
        None,
        "--password",
        "-p",
        help="Password for encrypted PDFs (BPI statements)"
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Parse without saving to database"
    ),
) -> None:
    """
    Parse bank statement PDF(s) and import transactions to database.

    Automatically detects bank type (GCash, BPI, Maya) from PDF content.
    Imports transactions to local SQLite database.

    Examples:
        # Parse single statement
        analyze-fin parse statement.pdf

        # Parse with password (BPI)
        analyze-fin parse bpi_statement.pdf --password SURNAME1234

        # Parse multiple files
        analyze-fin parse gcash.pdf bpi.pdf maya.pdf

        # Preview without saving
        analyze-fin parse statement.pdf --dry-run
    """
    from pathlib import Path

    from sqlalchemy.orm import Session

    from analyze_fin.database.models import Account, Statement, Transaction
    from analyze_fin.database.session import init_db
    from analyze_fin.parsers.batch import BatchImporter

    # Initialize database
    engine = init_db()

    # Convert string paths to Path objects
    paths = [Path(p) for p in pdf_paths]

    # Validate files exist
    for path in paths:
        if not path.exists():
            console.print(f"[red]Error:[/red] File not found: {path}")
            raise typer.Exit(code=1)

    console.print(f"[bold]Parsing {len(paths)} statement(s)...[/bold]\n")

    # Create importer and parse
    importer = BatchImporter()
    passwords = {str(p): password for p in paths} if password else {}

    try:
        result = importer.import_all(
            pdf_paths=paths,
            passwords=passwords,
            progress_callback=lambda curr, total, file, status: console.print(
                f"[dim]{curr}/{total}[/dim] {file.name}: {status}"
            )
        )

        # Display parsing results
        console.print()
        console.print("[green]✓[/green] Parsing complete!")
        console.print(f"  Total files: {result.total_files}")
        console.print(f"  Successful: {result.successful}")
        console.print(f"  Failed: {result.failed}")

        if result.successful > 0:
            console.print(f"  Quality: {result.get_confidence_label()} ({result.average_quality_score:.1%})")
            total_transactions = sum(len(r.transactions) for r in result.results)
            console.print(f"  Transactions: {total_transactions}")

        # Show errors if any
        if result.errors:
            console.print("\n[yellow]Errors:[/yellow]")
            for file_path, error in result.errors:
                console.print(f"  [red]✗[/red] {file_path}: {error}")

        # Show duplicates if any
        if result.duplicates:
            console.print("\n[dim]Skipped duplicates:[/dim]")
            for file_path, reason in result.duplicates:
                console.print(f"  [dim]→[/dim] {file_path}: {reason}")

        # Save to database (unless dry-run)
        if dry_run:
            console.print("\n[yellow]Dry run:[/yellow] Transactions not saved to database.")
        elif result.successful > 0:
            console.print("\n[bold]Saving to database...[/bold]")
            saved_count = 0
            skipped_count = 0

            with Session(engine) as session:
                try:
                    for parse_result in result.results:
                        # Get or create account based on bank type
                        bank_type = parse_result.bank_type
                        account = session.query(Account).filter_by(bank_type=bank_type).first()

                        if not account:
                            account = Account(
                                name=f"{bank_type.upper()} Account",
                                bank_type=bank_type,
                            )
                            session.add(account)
                            session.flush()  # Get account ID

                        # Check if statement already exists (by file path)
                        existing_stmt = session.query(Statement).filter_by(
                            file_path=str(parse_result.file_path)
                        ).first()

                        if existing_stmt:
                            console.print(f"  [dim]Skipped (exists):[/dim] {parse_result.file_path}")
                            skipped_count += len(parse_result.transactions)
                            continue

                        # Create statement record
                        statement = Statement(
                            account_id=account.id,
                            file_path=str(parse_result.file_path),
                            quality_score=parse_result.quality_score,
                        )
                        session.add(statement)
                        session.flush()  # Get statement ID

                        # Create transaction records
                        for raw_txn in parse_result.transactions:
                            txn = Transaction(
                                statement_id=statement.id,
                                date=raw_txn.date,
                                description=raw_txn.description,
                                amount=raw_txn.amount,
                                reference_number=raw_txn.reference_number,
                            )
                            session.add(txn)
                            saved_count += 1

                    session.commit()
                    console.print(f"[green]✓[/green] Saved {saved_count} transactions to database")
                    if skipped_count > 0:
                        console.print(f"[dim]  Skipped {skipped_count} (already imported)[/dim]")

                except Exception as e:
                    session.rollback()
                    console.print(f"[red]Error saving to database:[/red] {e}")
                    raise typer.Exit(code=1) from None

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error during parsing:[/red] {e}")
        raise typer.Exit(code=2) from None


@app.command()
def report(
    output_format: str = typer.Option(
        "summary",
        "--format",
        "-f",
        help="Report format: summary, html, markdown"
    ),
    output_path: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (prints to stdout if not provided)"
    ),
    date_range: str | None = typer.Option(
        None,
        "--date-range",
        "-d",
        help="Filter by date range (e.g., 'November 2024')"
    ),
    no_open: bool = typer.Option(
        False,
        "--no-open",
        help="Don't automatically open HTML reports in browser"
    ),
) -> None:
    """
    Generate spending report from transactions.

    Examples:
        # Print summary to console
        analyze-fin report

        # Generate HTML report
        analyze-fin report --format html --output report.html

        # Generate markdown report for specific month
        analyze-fin report --format markdown --date-range "November 2024"
    """
    from pathlib import Path

    from sqlalchemy.orm import Session

    from analyze_fin.analysis.spending import SpendingAnalyzer
    from analyze_fin.database.models import Transaction
    from analyze_fin.database.session import init_db

    # Parse date range if provided
    start_date: datetime | None = None
    end_date: datetime | None = None

    if date_range:
        try:
            start_date, end_date = _parse_date_range(date_range)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=2) from None

    # Initialize database and load transactions
    try:
        engine = init_db()
        with Session(engine) as session:
            # Load all transactions as dictionaries for analyzer
            query = session.query(Transaction)
            if start_date:
                query = query.filter(Transaction.date >= start_date)
            if end_date:
                query = query.filter(Transaction.date <= end_date)

            transactions = [
                {
                    "date": tx.date,
                    "description": tx.description,
                    "amount": tx.amount,
                    "category": tx.category,
                    "merchant_normalized": tx.merchant_normalized,
                }
                for tx in query.all()
            ]

            if not transactions:
                console.print("[yellow]No transactions found to report.[/yellow]")
                return

            # Generate report
            analyzer = SpendingAnalyzer()
            spending_report = analyzer.analyze(transactions)

            # Output based on format
            if output_format == "summary":
                _print_summary_report(spending_report)
            elif output_format in ("html", "markdown"):
                from analyze_fin.reports.generator import ReportGenerator

                generator = ReportGenerator()

                if output_format == "html":
                    content = generator.generate_html(
                        spending_report,
                        title="Spending Report",
                        start_date=start_date,
                        end_date=end_date,
                    )
                else:
                    content = generator.generate_markdown(
                        spending_report,
                        title="Spending Report",
                        start_date=start_date,
                        end_date=end_date,
                    )

                if output_path:
                    output_file = Path(output_path)
                    output_file.write_text(content, encoding="utf-8")
                    console.print(f"[green]✓[/green] Report saved to {output_path}")

                    # Auto-open HTML reports in browser unless --no-open flag is set
                    if output_format == "html" and not no_open:
                        import webbrowser
                        webbrowser.open(output_file.resolve().as_uri())
                        console.print("[dim]Opened report in browser[/dim]")
                else:
                    console.print(content)
            else:
                console.print(f"[red]Error:[/red] Invalid format '{output_format}'")
                console.print("[dim]Valid formats: summary, html, markdown[/dim]")
                raise typer.Exit(code=2)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error generating report:[/red] {e}")
        raise typer.Exit(code=1) from None


def _print_summary_report(report) -> None:
    """Print a summary report to console."""
    console.print("\n[bold]📊 Spending Report[/bold]\n")
    console.print(f"Total Transactions: {report.total_transactions}")
    console.print(f"Total Spent: ₱{report.total_spent:,.2f}")
    console.print(f"Average Transaction: ₱{report.average_transaction:,.2f}")

    if report.by_category:
        console.print("\n[bold]By Category:[/bold]")
        table = Table()
        table.add_column("Category", style="cyan")
        table.add_column("Count", justify="right")
        table.add_column("Total", justify="right", style="green")
        table.add_column("%", justify="right")

        sorted_cats = sorted(
            report.by_category.items(),
            key=lambda x: float(x[1]["total"]),
            reverse=True,
        )
        for cat, data in sorted_cats[:10]:
            table.add_row(
                cat,
                str(data["count"]),
                f"₱{data['total']:,.2f}",
                f"{data['percentage']:.1f}%",
            )
        console.print(table)

    if report.top_merchants:
        console.print("\n[bold]Top Merchants:[/bold]")
        table = Table()
        table.add_column("Merchant", style="cyan")
        table.add_column("Count", justify="right")
        table.add_column("Total", justify="right", style="green")

        for merchant in report.top_merchants[:5]:
            table.add_row(
                merchant["merchant"][:30],
                str(merchant["count"]),
                f"₱{merchant['total']:,.2f}",
            )
        console.print(table)


@app.command()
def export(
    output_format: str = typer.Option(
        "csv",
        "--format",
        "-f",
        help="Export format: csv, json"
    ),
    output_path: str | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (prints to stdout if not provided)"
    ),
    category: str | None = typer.Option(
        None,
        "--category",
        "-c",
        help="Filter by category"
    ),
    date_range: str | None = typer.Option(
        None,
        "--date-range",
        "-d",
        help="Filter by date range"
    ),
) -> None:
    """
    Export transactions to CSV or JSON.

    Examples:
        # Export all transactions to CSV
        analyze-fin export --format csv --output transactions.csv

        # Export JSON to stdout
        analyze-fin export --format json

        # Export filtered transactions
        analyze-fin export --category "Food & Dining" --format csv
    """
    from pathlib import Path

    from sqlalchemy.orm import Session

    from analyze_fin.database.session import init_db
    from analyze_fin.queries.spending import SpendingQuery

    # Parse date range
    start_date: datetime | None = None
    end_date: datetime | None = None

    if date_range:
        try:
            start_date, end_date = _parse_date_range(date_range)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(code=2) from None

    # Initialize database and query
    try:
        engine = init_db()
        with Session(engine) as session:
            query_builder = SpendingQuery(session)

            if category:
                query_builder = query_builder.filter_by_category(category)
            if start_date or end_date:
                query_builder = query_builder.filter_by_date_range(start_date, end_date)

            transactions = query_builder.execute()

            if output_format == "csv":
                output = _export_csv(transactions)
            elif output_format == "json":
                output = _export_json(transactions)
            else:
                console.print(f"[red]Error:[/red] Invalid format '{output_format}'")
                console.print("[dim]Valid formats: csv, json[/dim]")
                raise typer.Exit(code=2)

            if output_path:
                Path(output_path).write_text(output, encoding="utf-8")
                console.print(f"[green]✓[/green] Exported {len(transactions)} transactions to {output_path}")
            else:
                print(output)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error exporting:[/red] {e}")
        raise typer.Exit(code=1) from None


def _export_csv(transactions: list) -> str:
    """Export transactions to CSV string."""
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "description", "amount", "category", "merchant_normalized"])

    for tx in transactions:
        writer.writerow([
            tx.date.strftime("%Y-%m-%d"),
            tx.description,
            str(tx.amount),
            tx.category or "",
            tx.merchant_normalized or "",
        ])

    return output.getvalue()


def _export_json(transactions: list) -> str:
    """Export transactions to JSON string."""
    data = {
        "count": len(transactions),
        "transactions": [
            {
                "id": tx.id,
                "date": tx.date.strftime("%Y-%m-%d"),
                "description": tx.description,
                "amount": str(tx.amount),
                "category": tx.category,
                "merchant_normalized": tx.merchant_normalized,
            }
            for tx in transactions
        ],
    }
    return json.dumps(data, indent=2)


@app.command()
def categorize(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview categorization without saving"
    ),
    uncategorized_only: bool = typer.Option(
        True,
        "--uncategorized-only/--all",
        help="Only categorize uncategorized transactions"
    ),
) -> None:
    """
    Auto-categorize transactions using rule-based matching.

    Examples:
        # Preview categorization changes
        analyze-fin categorize --dry-run

        # Apply categorization to all uncategorized transactions
        analyze-fin categorize

        # Re-categorize all transactions
        analyze-fin categorize --all
    """
    from sqlalchemy.orm import Session

    from analyze_fin.categorization.categorizer import Categorizer
    from analyze_fin.database.models import Transaction
    from analyze_fin.database.session import init_db

    try:
        engine = init_db()
        with Session(engine) as session:
            # Query transactions
            query = session.query(Transaction)
            if uncategorized_only:
                query = query.filter(Transaction.category.is_(None))

            transactions = query.all()

            if not transactions:
                console.print("[yellow]No transactions to categorize.[/yellow]")
                return

            console.print(f"[bold]Categorizing {len(transactions)} transactions...[/bold]\n")

            categorizer = Categorizer()
            updates = []

            for tx in transactions:
                result = categorizer.categorize(tx.description)
                if result.category != "Uncategorized":
                    updates.append({
                        "tx": tx,
                        "category": result.category,
                        "merchant": result.merchant_normalized,
                        "confidence": result.confidence,
                        "method": result.method,
                    })

            if not updates:
                console.print("[yellow]No transactions could be categorized.[/yellow]")
                return

            # Display results
            table = Table(title=f"{'Preview: ' if dry_run else ''}Categorization Results")
            table.add_column("Date", style="cyan")
            table.add_column("Description")
            table.add_column("Category", style="green")
            table.add_column("Confidence", justify="right")

            for update in updates[:20]:  # Show first 20
                table.add_row(
                    update["tx"].date.strftime("%Y-%m-%d"),
                    update["tx"].description[:30] + ("..." if len(update["tx"].description) > 30 else ""),
                    update["category"],
                    f"{update['confidence']:.0%}",
                )

            console.print(table)

            if len(updates) > 20:
                console.print(f"[dim]... and {len(updates) - 20} more[/dim]")

            console.print(f"\n[bold]Total:[/bold] {len(updates)} transactions categorized")

            if not dry_run:
                # Apply updates
                for update in updates:
                    update["tx"].category = update["category"]
                    if update["merchant"]:
                        update["tx"].merchant_normalized = update["merchant"]

                session.commit()
                console.print("[green]✓[/green] Changes saved to database")
            else:
                console.print("[yellow]Dry run:[/yellow] No changes saved")

    except Exception as e:
        console.print(f"[red]Error categorizing:[/red] {e}")
        raise typer.Exit(code=1) from None


@app.command()
def deduplicate(
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--apply",
        help="Preview duplicates without removing (default: preview only)"
    ),
) -> None:
    """
    Detect and optionally remove duplicate transactions.

    Examples:
        # Preview duplicate detection
        analyze-fin deduplicate

        # Remove duplicates (requires confirmation)
        analyze-fin deduplicate --apply
    """
    from sqlalchemy.orm import Session

    from analyze_fin.database.models import Transaction
    from analyze_fin.database.session import init_db
    from analyze_fin.dedup.detector import DuplicateDetector

    try:
        engine = init_db()
        with Session(engine) as session:
            # Load all transactions
            transactions = session.query(Transaction).all()

            if not transactions:
                console.print("[yellow]No transactions to check for duplicates.[/yellow]")
                return

            console.print(f"[bold]Checking {len(transactions)} transactions for duplicates...[/bold]\n")

            # Convert to dict format for detector
            tx_dicts = [
                {
                    "id": tx.id,
                    "date": tx.date,
                    "description": tx.description,
                    "amount": tx.amount,
                    "reference_number": tx.reference_number,
                }
                for tx in transactions
            ]

            detector = DuplicateDetector()
            duplicates = detector.find_duplicates(tx_dicts)

            if not duplicates:
                console.print("[green]✓[/green] No duplicates found!")
                return

            console.print(f"[yellow]Found {len(duplicates)} potential duplicate pairs:[/yellow]\n")

            # Display duplicates
            table = Table(title="Duplicate Transactions")
            table.add_column("Type", style="cyan")
            table.add_column("Confidence", justify="right")
            table.add_column("Transaction A")
            table.add_column("Transaction B")

            for dup in duplicates[:10]:
                tx_a = dup.transaction_a
                tx_b = dup.transaction_b
                table.add_row(
                    dup.match_type,
                    f"{dup.confidence:.0%}",
                    f"{tx_a['date'].strftime('%Y-%m-%d')}: {tx_a['description'][:20]}...",
                    f"{tx_b['date'].strftime('%Y-%m-%d')}: {tx_b['description'][:20]}...",
                )

            console.print(table)

            if len(duplicates) > 10:
                console.print(f"[dim]... and {len(duplicates) - 10} more[/dim]")

            if dry_run:
                console.print("\n[yellow]Dry run:[/yellow] Use --apply to remove duplicates")
            else:
                console.print("\n[yellow]Note:[/yellow] Automatic removal not yet implemented.")
                console.print("[dim]Please review duplicates manually and remove via SQL if needed.[/dim]")

    except Exception as e:
        console.print(f"[red]Error detecting duplicates:[/red] {e}")
        raise typer.Exit(code=1) from None


@app.command()
def ask(
    question: str = typer.Argument(
        ...,
        help="Natural language question about your spending"
    ),
    output_format: str = typer.Option(
        "pretty",
        "--format",
        "-f",
        help="Output format: pretty, json"
    ),
) -> None:
    """
    Ask questions about your spending in natural language.

    Uses AI-powered parsing to understand your question and query the database.

    Examples:
        # Ask about category spending
        analyze-fin ask "How much did I spend on food?"

        # Query by merchant
        analyze-fin ask "Show transactions from Jollibee"

        # Time-based queries
        analyze-fin ask "What did I buy last month?"

        # Amount filters
        analyze-fin ask "Transactions over 1000 pesos"

        # Complex queries
        analyze-fin ask "Food expenses in November over 500"
    """
    from sqlalchemy.orm import Session

    from analyze_fin.database.session import init_db
    from analyze_fin.queries.nl_parser import NLQueryParser
    from analyze_fin.queries.spending import SpendingQuery

    # Parse the natural language question
    parser = NLQueryParser()
    parsed = parser.parse(question)

    # Show what was understood
    console.print(f"\n[dim]Understood:[/dim]")
    if parsed.category:
        console.print(f"  [cyan]Category:[/cyan] {parsed.category}")
    if parsed.merchant:
        console.print(f"  [cyan]Merchant:[/cyan] {parsed.merchant}")
    if parsed.start_date:
        console.print(f"  [cyan]From:[/cyan] {parsed.start_date.strftime('%Y-%m-%d')}")
    if parsed.end_date:
        console.print(f"  [cyan]To:[/cyan] {parsed.end_date.strftime('%Y-%m-%d')}")
    if parsed.min_amount:
        console.print(f"  [cyan]Min amount:[/cyan] ₱{parsed.min_amount:,.2f}")
    if parsed.max_amount:
        console.print(f"  [cyan]Max amount:[/cyan] ₱{parsed.max_amount:,.2f}")
    console.print(f"  [cyan]Intent:[/cyan] {parsed.intent}")
    console.print()

    # Initialize database and run query
    try:
        engine = init_db()
        with Session(engine) as session:
            query_builder = SpendingQuery(session)

            # Apply parsed filters
            if parsed.category:
                query_builder = query_builder.filter_by_category(parsed.category)
            if parsed.merchant:
                query_builder = query_builder.filter_by_merchant(parsed.merchant)
            if parsed.start_date or parsed.end_date:
                query_builder = query_builder.filter_by_date_range(
                    parsed.start_date, parsed.end_date
                )
            if parsed.min_amount is not None or parsed.max_amount is not None:
                query_builder = query_builder.filter_by_amount(
                    parsed.min_amount, parsed.max_amount
                )

            # Execute based on intent
            if parsed.intent == "total":
                total = query_builder.total_amount()
                count = query_builder.count()
                console.print(f"[bold green]Total:[/bold green] ₱{total:,.2f}")
                console.print(f"[dim]({count} transactions)[/dim]")

            elif parsed.intent == "count":
                count = query_builder.count()
                console.print(f"[bold green]Count:[/bold green] {count} transactions")

            elif parsed.intent == "average":
                total = query_builder.total_amount()
                count = query_builder.count()
                if count > 0:
                    avg = total / count
                    console.print(f"[bold green]Average:[/bold green] ₱{avg:,.2f}")
                    console.print(f"[dim]({count} transactions totaling ₱{total:,.2f})[/dim]")
                else:
                    console.print("[yellow]No transactions found[/yellow]")

            else:  # list
                transactions = query_builder.execute()
                total = query_builder.total_amount()
                count = len(transactions)

                if output_format == "json":
                    _output_json(transactions, count, total)
                else:
                    _output_pretty(
                        transactions, count, total,
                        parsed.category, parsed.merchant,
                        f"{parsed.start_date} to {parsed.end_date}" if parsed.start_date else None
                    )

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=1) from None


@app.command()
def version() -> None:
    """Show version information."""
    console.print("[bold]analyze-fin[/bold] version 0.1.0")
    console.print("Philippine Personal Finance Tracker")


def main() -> None:
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
