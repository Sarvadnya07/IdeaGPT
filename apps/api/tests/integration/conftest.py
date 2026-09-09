"""
Pytest configuration specifically for PostgreSQL integration tests.
Overrides unit-test SQLite fixtures to prevent interference.
"""

import pytest

@pytest.fixture(autouse=True)
def setup_test_db():
    """Override unit test SQLite autouse fixture for PostgreSQL integration tests."""
    yield

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
