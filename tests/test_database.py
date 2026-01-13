"""Tests for SQLite database operations."""

import pytest
from datetime import datetime


class TestDatabaseBudgets:
    """Tests for budget operations."""

    def test_upsert_and_get_budget(self, temp_db):
        """Test inserting and retrieving a budget."""
        temp_db.upsert_budget(
            budget_id="budget-001",
            name="Test Budget",
            last_modified_on="2024-01-15T10:00:00Z",
            first_month="2023-01-01",
            last_month="2024-01-01",
            currency_format=None
        )

        budgets = temp_db.get_budgets()
        assert len(budgets) == 1
        assert budgets[0]['id'] == "budget-001"
        assert budgets[0]['name'] == "Test Budget"

    def test_get_nonexistent_budget(self, temp_db):
        """Test getting a budget that doesn't exist."""
        budget = temp_db.get_budget("nonexistent")
        assert budget is None


class TestDatabaseTransactions:
    """Tests for transaction operations."""

    def test_upsert_transaction(self, temp_db, sample_transaction):
        """Test inserting a transaction."""
        temp_db.upsert_transaction(
            txn_id=sample_transaction['id'],
            budget_id=sample_transaction['budget_id'],
            account_id=sample_transaction['account_id'],
            account_name=sample_transaction['account_name'],
            txn_date=sample_transaction['date'],
            amount=sample_transaction['amount'],
            memo=sample_transaction['memo'],
            cleared=sample_transaction['cleared'],
            approved=sample_transaction['approved'],
            flag_color=sample_transaction['flag_color'],
            payee_id=sample_transaction['payee_id'],
            payee_name=sample_transaction['payee_name'],
            category_id=sample_transaction['category_id'],
            category_name=sample_transaction['category_name'],
            transfer_account_id=sample_transaction['transfer_account_id'],
            transfer_transaction_id=sample_transaction['transfer_transaction_id'],
            import_id=sample_transaction['import_id'],
            deleted=sample_transaction['deleted']
        )

        txns = temp_db.get_transactions(sample_transaction['budget_id'])
        assert len(txns) == 1
        assert txns[0]['id'] == sample_transaction['id']
        assert txns[0]['amount'] == -50000

    def test_get_recent_transactions(self, temp_db, sample_transaction):
        """Test retrieving recent transactions."""
        # Insert with today's date
        sample_transaction['date'] = datetime.now().strftime('%Y-%m-%d')
        temp_db.upsert_transaction(
            txn_id=sample_transaction['id'],
            budget_id=sample_transaction['budget_id'],
            account_id=sample_transaction['account_id'],
            account_name=sample_transaction['account_name'],
            txn_date=sample_transaction['date'],
            amount=sample_transaction['amount'],
            memo=sample_transaction['memo'],
            cleared=sample_transaction['cleared'],
            approved=sample_transaction['approved'],
            flag_color=sample_transaction['flag_color'],
            payee_id=sample_transaction['payee_id'],
            payee_name=sample_transaction['payee_name'],
            category_id=sample_transaction['category_id'],
            category_name=sample_transaction['category_name'],
            transfer_account_id=sample_transaction['transfer_account_id'],
            transfer_transaction_id=sample_transaction['transfer_transaction_id'],
            import_id=sample_transaction['import_id'],
            deleted=sample_transaction['deleted']
        )

        recent = temp_db.get_recent_transactions(sample_transaction['budget_id'], days=7)
        assert len(recent) == 1


class TestDatabaseCategories:
    """Tests for category operations."""

    def test_upsert_category(self, temp_db, sample_category):
        """Test inserting a category."""
        temp_db.upsert_category(
            category_id=sample_category['id'],
            budget_id=sample_category['budget_id'],
            category_group_id=sample_category['category_group_id'],
            category_group_name=sample_category['category_group_name'],
            name=sample_category['name'],
            hidden=sample_category['hidden'],
            budgeted=sample_category['budgeted'],
            activity=sample_category['activity'],
            balance=sample_category['balance'],
            goal_type=sample_category['goal_type'],
            goal_target=sample_category['goal_target'],
            goal_target_month=sample_category['goal_target_month']
        )

        categories = temp_db.get_categories(sample_category['budget_id'])
        assert len(categories) == 1
        assert categories[0]['name'] == "Groceries"
        assert categories[0]['budgeted'] == 500000


class TestDatabaseAlerts:
    """Tests for alert operations."""

    def test_save_and_get_alert(self, temp_db, sample_budget_id):
        """Test saving and retrieving alerts."""
        alert_id = temp_db.save_alert(
            budget_id=sample_budget_id,
            alert_type="unusual_spending",
            severity="warning",
            title="Test Alert",
            description="This is a test alert",
            related_entity_id="txn-001",
            related_entity_type="transaction",
            metadata={"test": "data"}
        )

        assert alert_id is not None

        alerts = temp_db.get_alerts(sample_budget_id)
        assert len(alerts) == 1
        assert alerts[0]['title'] == "Test Alert"
        assert alerts[0]['severity'] == "warning"

    def test_dismiss_alert(self, temp_db, sample_budget_id):
        """Test dismissing an alert."""
        alert_id = temp_db.save_alert(
            budget_id=sample_budget_id,
            alert_type="budget_overspending",
            severity="critical",
            title="Over Budget",
            description="You're over budget"
        )

        temp_db.dismiss_alert(alert_id)

        # Should not appear in default query
        alerts = temp_db.get_alerts(sample_budget_id, include_dismissed=False)
        assert len(alerts) == 0

        # Should appear when including dismissed
        alerts = temp_db.get_alerts(sample_budget_id, include_dismissed=True)
        assert len(alerts) == 1
        assert alerts[0]['dismissed'] == 1

    def test_alert_exists(self, temp_db, sample_budget_id):
        """Test checking if alert exists."""
        temp_db.save_alert(
            budget_id=sample_budget_id,
            alert_type="recurring_change",
            severity="info",
            title="Recurring Changed",
            description="Amount changed",
            related_entity_id="sched-001"
        )

        exists = temp_db.alert_exists(sample_budget_id, "recurring_change", "sched-001")
        assert exists is True

        not_exists = temp_db.alert_exists(sample_budget_id, "recurring_change", "sched-999")
        assert not_exists is False


class TestDatabaseSyncMetadata:
    """Tests for sync metadata operations."""

    def test_sync_knowledge(self, temp_db, sample_budget_id):
        """Test sync knowledge tracking."""
        # Initially should be None
        knowledge = temp_db.get_sync_knowledge(sample_budget_id, "transactions")
        assert knowledge is None

        # Update knowledge
        temp_db.update_sync_knowledge(sample_budget_id, "transactions", 12345)

        # Should return updated value
        knowledge = temp_db.get_sync_knowledge(sample_budget_id, "transactions")
        assert knowledge == 12345

    def test_last_sync(self, temp_db, sample_budget_id):
        """Test last sync timestamp."""
        # Initially should be None
        last_sync = temp_db.get_last_sync(sample_budget_id)
        assert last_sync is None

        # Update sync knowledge (which updates timestamp)
        temp_db.update_sync_knowledge(sample_budget_id, "accounts", 100)

        # Should have a timestamp now
        last_sync = temp_db.get_last_sync(sample_budget_id)
        assert last_sync is not None
