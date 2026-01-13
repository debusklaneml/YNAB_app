"""Tests for formatting utilities."""

import pytest
from decimal import Decimal
from datetime import date, datetime

from src.utils.formatters import (
    milliunits_to_dollars,
    dollars_to_milliunits,
    format_currency,
    format_date,
    format_month,
    get_current_month,
    format_percentage,
    format_change
)


class TestMilliunitsConversion:
    """Tests for milliunits conversion functions."""

    def test_milliunits_to_dollars_positive(self):
        """Test converting positive milliunits to dollars."""
        result = milliunits_to_dollars(50000)
        assert result == Decimal("50.000")

    def test_milliunits_to_dollars_negative(self):
        """Test converting negative milliunits to dollars."""
        result = milliunits_to_dollars(-25500)
        assert result == Decimal("-25.500")

    def test_milliunits_to_dollars_zero(self):
        """Test converting zero."""
        result = milliunits_to_dollars(0)
        assert result == Decimal("0")

    def test_dollars_to_milliunits(self):
        """Test converting dollars to milliunits."""
        result = dollars_to_milliunits(Decimal("50.00"))
        assert result == 50000

    def test_dollars_to_milliunits_from_float(self):
        """Test converting float dollars to milliunits."""
        result = dollars_to_milliunits(25.50)
        assert result == 25500


class TestFormatCurrency:
    """Tests for currency formatting."""

    def test_format_positive_amount(self):
        """Test formatting positive amount."""
        result = format_currency(50000)
        assert result == "$50.00"

    def test_format_negative_amount(self):
        """Test formatting negative amount."""
        result = format_currency(-25000)
        assert result == "-$25.00"

    def test_format_with_sign_positive(self):
        """Test formatting with sign for positive."""
        result = format_currency(50000, show_sign=True)
        assert result == "+$50.00"

    def test_format_large_amount(self):
        """Test formatting large amount with commas."""
        result = format_currency(1234567890)
        assert result == "$1,234,567.89"


class TestFormatDate:
    """Tests for date formatting."""

    def test_format_date_object(self):
        """Test formatting a date object."""
        d = date(2024, 1, 15)
        result = format_date(d)
        assert result == "Jan 15, 2024"

    def test_format_datetime_object(self):
        """Test formatting a datetime object."""
        dt = datetime(2024, 6, 30, 12, 0, 0)
        result = format_date(dt)
        assert result == "Jun 30, 2024"

    def test_format_date_string(self):
        """Test formatting a date string."""
        result = format_date("2024-03-20")
        assert result == "Mar 20, 2024"


class TestFormatMonth:
    """Tests for month formatting."""

    def test_format_month(self):
        """Test formatting a month string."""
        result = format_month("2024-01-01")
        assert result == "January 2024"

    def test_format_invalid_month(self):
        """Test formatting an invalid month string."""
        result = format_month("invalid")
        assert result == "invalid"


class TestGetCurrentMonth:
    """Tests for current month function."""

    def test_current_month_format(self):
        """Test that current month returns correct format."""
        result = get_current_month()
        # Should be in YYYY-MM-01 format
        assert len(result) == 10
        assert result.endswith("-01")
        assert result[4] == "-"
        assert result[7] == "-"


class TestFormatPercentage:
    """Tests for percentage formatting."""

    def test_format_percentage(self):
        """Test formatting a percentage."""
        result = format_percentage(0.5)
        assert result == "50.0%"

    def test_format_percentage_with_decimals(self):
        """Test formatting with specific decimal places."""
        result = format_percentage(0.1234, decimals=2)
        assert result == "12.34%"


class TestFormatChange:
    """Tests for change formatting."""

    def test_format_positive_change(self):
        """Test formatting a positive change."""
        result = format_change(100, 80)
        assert "+" in result or result.startswith("25")

    def test_format_negative_change(self):
        """Test formatting a negative change."""
        result = format_change(80, 100)
        assert "-" in result

    def test_format_zero_previous(self):
        """Test formatting when previous is zero."""
        result = format_change(100, 0)
        assert "100%" in result

    def test_format_no_change(self):
        """Test formatting when there's no change."""
        result = format_change(0, 0)
        assert result == "0%"
