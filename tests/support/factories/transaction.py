import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from analyze_fin.database.models import Transaction

def create_transaction(
    statement_id: int | None = None,
    amount: Decimal | str | float | None = None,
    date: datetime | None = None,
    **overrides
) -> Transaction:
    """Create a Transaction model instance with random data."""
    
    # Handle amount types
    if amount is not None:
        if isinstance(amount, (float, str, int)):
            amount = Decimal(str(amount))
    else:
        amount = Decimal(f"{random.uniform(10.0, 5000.0):.2f}")
        
    categories = ["Food & Dining", "Transportation", "Shopping", "Bills", "Groceries", None]
    merchants = ["Jollibee", "Grab", "7-Eleven", "Meralco", "SM Supermarket", "Unknown"]
    
    defaults = {
        "statement_id": statement_id or random.randint(1, 1000),
        "date": date or datetime.now() - timedelta(days=random.randint(0, 30)),
        "description": f"Transaction {uuid.uuid4().hex[:8]}",
        "amount": amount,
        "created_at": datetime.now(),
        "category": random.choice(categories),
        "merchant_normalized": random.choice(merchants),
        "confidence": Decimal(f"{random.uniform(0.7, 1.0):.2f}"),
        "reference_number": f"REF{random.randint(100000, 999999)}",
        "is_duplicate": False,
        "duplicate_of_id": None,
    }
    
    defaults.update(overrides)
    return Transaction(**defaults)

