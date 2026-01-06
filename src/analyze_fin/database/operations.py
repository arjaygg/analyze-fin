"""Database operations for analyze-fin.

Provides helper functions for common database operations,
particularly for multi-account support (Story 5.2).
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from analyze_fin.database.models import Account


def get_or_create_account(
    session: Session,
    bank_type: str,
    account_number: str | None = None,
    account_holder: str | None = None,
) -> Account:
    """Get existing account or create new one.

    Matches on (bank_type, account_number) pair. If account_number is None,
    looks for legacy accounts with null account_number.

    This function handles race conditions by catching IntegrityError
    and retrying the lookup if a concurrent insert occurred.

    Args:
        session: SQLAlchemy session
        bank_type: Bank type (gcash, bpi, maya_savings, maya_wallet)
        account_number: Bank account number or mobile number (optional)
        account_holder: Account holder name (optional)

    Returns:
        Account: Existing or newly created account
    """

    def _find_account() -> Account | None:
        """Find existing account by bank_type and account_number."""
        query = session.query(Account).filter(Account.bank_type == bank_type)
        if account_number:
            query = query.filter(Account.account_number == account_number)
        else:
            query = query.filter(Account.account_number.is_(None))
        return query.first()

    # First attempt: find existing account
    account = _find_account()

    if account:
        # Update holder name if provided and not already set
        if account_holder and not account.account_holder:
            account.account_holder = account_holder
            session.flush()  # Ensure update is persisted
        return account

    # Create new account with appropriate name
    name = _generate_account_name(bank_type, account_number, account_holder)

    account = Account(
        name=name,
        bank_type=bank_type,
        account_number=account_number,
        account_holder=account_holder,
    )
    session.add(account)

    try:
        session.flush()  # Try to persist - may fail if concurrent insert
    except IntegrityError:
        # Race condition: another process created the account
        session.rollback()
        account = _find_account()
        if account is None:
            # Should not happen, but re-raise if it does
            raise
        # Update holder if needed
        if account_holder and not account.account_holder:
            account.account_holder = account_holder
            session.flush()

    return account


def _generate_account_name(
    bank_type: str,
    account_number: str | None,
    account_holder: str | None,
) -> str:
    """Generate display name for a new account.

    Priority:
    1. "Holder Name (BANK)" if holder is available
    2. "BANK ****1234" if account number is available
    3. "BANK Account" as fallback

    Args:
        bank_type: Bank type
        account_number: Bank account number (optional)
        account_holder: Account holder name (optional)

    Returns:
        Generated account name
    """
    bank_upper = bank_type.upper()

    if account_holder:
        return f"{account_holder} ({bank_upper})"
    elif account_number:
        masked = _mask_account_number(account_number)
        return f"{bank_upper} {masked}"
    else:
        return f"{bank_upper} Account"


def _mask_account_number(account_number: str) -> str:
    """Mask account number for display, showing only last 4 digits.

    Args:
        account_number: Full account number

    Returns:
        Masked account number like "****1234"
    """
    if len(account_number) >= 4:
        return f"****{account_number[-4:]}"
    return account_number


def get_account_display_name(account: Account) -> str:
    """Get display name for an account with fallback for legacy data.

    Format:
    - "Holder Name (BANK ****1234)" if holder and number available
    - "Holder Name (BANK)" if only holder available
    - "BANK ****1234" if only number available
    - "BANK (Unknown Account)" for legacy data without number/holder

    Args:
        account: Account model instance

    Returns:
        Human-readable display name
    """
    bank_upper = account.bank_type.upper()

    if account.account_holder and account.account_number:
        masked = _mask_account_number(account.account_number)
        return f"{account.account_holder} ({bank_upper} {masked})"
    elif account.account_holder:
        return f"{account.account_holder} ({bank_upper})"
    elif account.account_number:
        masked = _mask_account_number(account.account_number)
        return f"{bank_upper} {masked}"
    else:
        return f"{bank_upper} (Unknown Account)"
