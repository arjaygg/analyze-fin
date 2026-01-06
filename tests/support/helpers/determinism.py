from __future__ import annotations

import os
import random
import uuid
from datetime import datetime

DEFAULT_TEST_SEED = 0
# Chosen to align with existing fixture dates in the repo; keep as naive datetime.
DEFAULT_TEST_NOW = datetime(2024, 11, 30, 0, 0, 0)


def get_test_seed() -> int:
    """Return the test seed used to make random-dependent tests reproducible."""
    raw = os.environ.get("TEST_SEED", str(DEFAULT_TEST_SEED))
    try:
        return int(raw)
    except ValueError:
        return DEFAULT_TEST_SEED


def seed_python_random(seed: int | None = None) -> int:
    """Seed Python's global random module and return the seed used."""
    used = get_test_seed() if seed is None else seed
    random.seed(used)
    return used


def get_test_now() -> datetime:
    """
    Return a deterministic 'now' timestamp for tests.

    Override with TEST_NOW (ISO string) if needed, e.g.:
      TEST_NOW=2024-11-30T00:00:00
    """
    raw = os.environ.get("TEST_NOW")
    if not raw:
        return DEFAULT_TEST_NOW
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return DEFAULT_TEST_NOW


def deterministic_uuid_hex(length: int = 8) -> str:
    """Return a deterministic hex string derived from the global random seed."""
    # uuid4() uses OS entropy; use seeded random bits instead for reproducibility.
    u = uuid.UUID(int=random.getrandbits(128))
    return u.hex[:length]



