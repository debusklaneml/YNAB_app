"""Pytest fixtures for YNAB App tests."""

import pytest
import tempfile
from pathlib import Path

from src.cache.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        db = Database(db_path)
        yield db


@pytest.fixture
def sample_budget_id():
    """Sample budget ID for testing."""
    return "test-budget-123"


@pytest.fixture
def sample_transaction():
    """Sample transaction data."""
    return {
        'id': 'txn-001',
        'budget_id': 'test-budget-123',
        'account_id': 'acc-001',
        'account_name': 'Checking',
        'date': '2024-01-15',
        'amount': -50000,  # -$50.00 in milliunits
        'memo': 'Test transaction',
        'cleared': 'cleared',
        'approved': True,
        'flag_color': None,
        'payee_id': 'payee-001',
        'payee_name': 'Test Store',
        'category_id': 'cat-001',
        'category_name': 'Groceries',
        'transfer_account_id': None,
        'transfer_transaction_id': None,
        'import_id': None,
        'deleted': False
    }


@pytest.fixture
def sample_category():
    """Sample category data."""
    return {
        'id': 'cat-001',
        'budget_id': 'test-budget-123',
        'category_group_id': 'group-001',
        'category_group_name': 'Everyday Expenses',
        'name': 'Groceries',
        'hidden': False,
        'budgeted': 500000,  # $500.00 in milliunits
        'activity': -250000,  # -$250.00 spent
        'balance': 250000,
        'goal_type': None,
        'goal_target': None,
        'goal_target_month': None
    }
