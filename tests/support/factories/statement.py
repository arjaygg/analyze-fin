import random
import uuid
from datetime import datetime
from decimal import Decimal

from analyze_fin.database.models import Statement

def create_statement(
    account_id: int | None = None,
    file_path: str | None = None,
    **overrides
) -> Statement:
    """Create a Statement model instance with random data."""
    defaults = {
        "account_id": account_id or random.randint(1, 1000),
        "file_path": file_path or f"/tmp/statement_{uuid.uuid4().hex[:8]}.pdf",
        "imported_at": datetime.now(),
        "quality_score": Decimal(f"{random.uniform(0.5, 1.0):.2f}"),
    }
    
    defaults.update(overrides)
    return Statement(**defaults)

