import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from analyze_fin.database.models import Account

def create_account(
    name: str | None = None,
    bank_type: str | None = None,
    **overrides
) -> Account:
    """Create an Account model instance with random data."""
    bank_types = ["gcash", "bpi", "maya", "maya_savings", "maya_wallet"]
    
    defaults = {
        "name": name or f"Test Account {uuid.uuid4().hex[:8]}",
        "bank_type": bank_type or random.choice(bank_types),
        "created_at": datetime.now(),
    }
    
    defaults.update(overrides)
    return Account(**defaults)

