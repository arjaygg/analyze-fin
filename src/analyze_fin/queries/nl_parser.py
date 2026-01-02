"""
Natural language query parser for spending queries.

Parses natural language questions into SpendingQuery filter parameters.

Supports patterns like:
- "How much did I spend on food?"
- "Show transactions over 1000 pesos"
- "What did I buy from Jollibee last month?"
- "Food expenses in November 2024"
"""

import calendar
import re
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation


@dataclass
class ParsedQuery:
    """Result of parsing a natural language query.

    Attributes:
        category: Extracted category filter (if found)
        merchant: Extracted merchant filter (if found)
        start_date: Start of date range (if found)
        end_date: End of date range (if found)
        min_amount: Minimum amount filter (if found)
        max_amount: Maximum amount filter (if found)
        original_query: The original query text
        intent: Detected query intent (list, total, count, etc.)
    """

    category: str | None = None
    merchant: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    original_query: str = ""
    intent: str = "list"  # list, total, count, average


# Category keywords mapping
CATEGORY_KEYWORDS = {
    "food": "Food & Dining",
    "dining": "Food & Dining",
    "eat": "Food & Dining",
    "restaurant": "Food & Dining",
    "groceries": "Groceries",
    "grocery": "Groceries",
    "transport": "Transportation",
    "transportation": "Transportation",
    "grab": "Transportation",
    "uber": "Transportation",
    "taxi": "Transportation",
    "ride": "Transportation",
    "shopping": "Shopping",
    "shop": "Shopping",
    "buy": "Shopping",
    "bills": "Bills & Utilities",
    "bill": "Bills & Utilities",
    "utilities": "Bills & Utilities",
    "electric": "Bills & Utilities",
    "water": "Bills & Utilities",
    "internet": "Bills & Utilities",
    "entertainment": "Entertainment",
    "movie": "Entertainment",
    "games": "Entertainment",
    "health": "Health & Medical",
    "medical": "Health & Medical",
    "medicine": "Health & Medical",
    "transfer": "Transfers",
    "send": "Transfers",
    "sent": "Transfers",
}

# Month name patterns
MONTH_NAMES = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}


class NLQueryParser:
    """Parse natural language queries into structured filter parameters.

    Example:
        parser = NLQueryParser()
        result = parser.parse("How much did I spend on food in November?")
        print(f"Category: {result.category}")
        print(f"Date range: {result.start_date} to {result.end_date}")
    """

    def parse(self, query: str) -> ParsedQuery:
        """Parse a natural language query into filter parameters.

        Args:
            query: Natural language question about spending

        Returns:
            ParsedQuery with extracted filters
        """
        result = ParsedQuery(original_query=query)
        query_lower = query.lower()

        # Detect intent
        result.intent = self._detect_intent(query_lower)

        # Extract category
        result.category = self._extract_category(query_lower)

        # Extract merchant
        result.merchant = self._extract_merchant(query, query_lower)

        # Extract date range
        start_date, end_date = self._extract_date_range(query_lower)
        result.start_date = start_date
        result.end_date = end_date

        # Extract amount
        min_amount, max_amount = self._extract_amount(query_lower)
        result.min_amount = min_amount
        result.max_amount = max_amount

        return result

    def _detect_intent(self, query: str) -> str:
        """Detect the query intent."""
        if any(word in query for word in ["how much", "total", "spent", "spend"]):
            return "total"
        elif any(word in query for word in ["how many", "count", "number of"]):
            return "count"
        elif any(word in query for word in ["average", "avg", "mean"]):
            return "average"
        else:
            return "list"

    def _extract_category(self, query: str) -> str | None:
        """Extract category from query."""
        # Look for category keywords
        for keyword, category in CATEGORY_KEYWORDS.items():
            if keyword in query:
                return category
        return None

    def _extract_merchant(self, original: str, query_lower: str) -> str | None:
        """Extract merchant name from query.

        Looks for patterns like:
        - "from Jollibee"
        - "at McDonald's"
        - "to GCash"
        """
        # Pattern: "from/at/to {Merchant}"
        patterns = [
            r"(?:from|at|to)\s+([A-Z][a-zA-Z']+(?:\s+[A-Z][a-zA-Z']+)?)",
            r"(?:from|at|to)\s+(\w+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, original)
            if match:
                merchant = match.group(1)
                # Filter out common words
                if merchant.lower() not in {"the", "a", "an", "my", "our", "their"}:
                    return merchant

        return None

    def _extract_date_range(self, query: str) -> tuple[datetime | None, datetime | None]:
        """Extract date range from query."""
        now = datetime.now()
        current_year = now.year

        # "last month"
        if "last month" in query:
            if now.month == 1:
                year = current_year - 1
                month = 12
            else:
                year = current_year
                month = now.month - 1
            start = datetime(year, month, 1)
            _, last_day = calendar.monthrange(year, month)
            end = datetime(year, month, last_day)
            return start, end

        # "this month"
        if "this month" in query:
            start = datetime(current_year, now.month, 1)
            _, last_day = calendar.monthrange(current_year, now.month)
            end = datetime(current_year, now.month, last_day)
            return start, end

        # "last week"
        if "last week" in query:
            from datetime import timedelta
            start = now - timedelta(days=now.weekday() + 7)
            end = start + timedelta(days=6)
            return datetime(start.year, start.month, start.day), datetime(end.year, end.month, end.day)

        # "this week"
        if "this week" in query:
            from datetime import timedelta
            start = now - timedelta(days=now.weekday())
            end = now
            return datetime(start.year, start.month, start.day), datetime(end.year, end.month, end.day)

        # "today"
        if "today" in query:
            start = datetime(now.year, now.month, now.day)
            return start, start

        # "yesterday"
        if "yesterday" in query:
            from datetime import timedelta
            yesterday = now - timedelta(days=1)
            start = datetime(yesterday.year, yesterday.month, yesterday.day)
            return start, start

        # Month name pattern: "in November" or "November 2024"
        for month_name, month_num in MONTH_NAMES.items():
            if month_name in query:
                # Try to find year
                year_match = re.search(r"20\d{2}", query)
                if year_match:
                    year = int(year_match.group())
                else:
                    # Default to current year, or last year if month is future
                    year = current_year
                    if month_num > now.month:
                        year -= 1

                start = datetime(year, month_num, 1)
                _, last_day = calendar.monthrange(year, month_num)
                end = datetime(year, month_num, last_day)
                return start, end

        # Date pattern: "2024-11-01 to 2024-11-30"
        date_range_match = re.search(
            r"(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})",
            query
        )
        if date_range_match:
            start = datetime.strptime(date_range_match.group(1), "%Y-%m-%d")
            end = datetime.strptime(date_range_match.group(2), "%Y-%m-%d")
            return start, end

        return None, None

    def _extract_amount(self, query: str) -> tuple[Decimal | None, Decimal | None]:
        """Extract amount filters from query."""
        min_amount = None
        max_amount = None

        # "over/above/more than X" pattern
        over_pattern = r"(?:over|above|more than|greater than|at least)\s*[₱P]?(\d+(?:,\d{3})*(?:\.\d{2})?)"
        over_match = re.search(over_pattern, query)
        if over_match:
            try:
                min_amount = Decimal(over_match.group(1).replace(",", ""))
            except InvalidOperation:
                pass

        # "under/below/less than X" pattern
        under_pattern = r"(?:under|below|less than|at most)\s*[₱P]?(\d+(?:,\d{3})*(?:\.\d{2})?)"
        under_match = re.search(under_pattern, query)
        if under_match:
            try:
                max_amount = Decimal(under_match.group(1).replace(",", ""))
            except InvalidOperation:
                pass

        # "between X and Y" pattern
        between_pattern = r"between\s*[₱P]?(\d+(?:,\d{3})*(?:\.\d{2})?)\s+and\s*[₱P]?(\d+(?:,\d{3})*(?:\.\d{2})?)"
        between_match = re.search(between_pattern, query)
        if between_match:
            try:
                min_amount = Decimal(between_match.group(1).replace(",", ""))
                max_amount = Decimal(between_match.group(2).replace(",", ""))
            except InvalidOperation:
                pass

        return min_amount, max_amount


def parse_natural_language_query(query: str) -> ParsedQuery:
    """Convenience function to parse a natural language query.

    Args:
        query: Natural language question about spending

    Returns:
        ParsedQuery with extracted filters
    """
    parser = NLQueryParser()
    return parser.parse(query)

