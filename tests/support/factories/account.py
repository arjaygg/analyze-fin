import random

from analyze_fin.database.models import Account
from tests.support.helpers.determinism import deterministic_uuid_hex, get_test_now


def create_account(
    name: str | None = None,
    bank_type: str | None = None,
    **overrides
) -> Account:
    """Create an Account model instance with random data."""
    bank_types = ["gcash", "bpi", "maya", "maya_savings", "maya_wallet"]

    defaults = {
        "name": name or f"Test Account {deterministic_uuid_hex()}",
        "bank_type": bank_type or random.choice(bank_types),
        "created_at": get_test_now(),
    }

    defaults.update(overrides)
    return Account(**defaults)

