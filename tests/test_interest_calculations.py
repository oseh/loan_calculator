
import pytest
from datetime import datetime
from loan_calculator.data_store import CalculationData
from loan_calculator.interest_calculations import (
    parse_date,
    is_weekend,
    simple_interest_daily,
    daily_interest_data,
    total_interest
)

@pytest.fixture
def simple_calc():
    return CalculationData(
        start_date="2024-01-01",
        end_date="2024-01-10",
        amount=1000.0,
        currency="USD",
        base_rate=5.0,
        margin=2.0,
        exclude_weekends=False,
        method="simple"
    )

@pytest.fixture
def compound_calc():
    return CalculationData(
        start_date="2024-01-01",
        end_date="2024-01-10",
        amount=1000.0,
        currency="USD",
        base_rate=5.0,
        margin=2.0,
        exclude_weekends=False,
        method="compound"
    )

@pytest.fixture
def exclude_weekends_calc():
    return CalculationData(
        start_date="2024-01-01",
        end_date="2024-01-10",
        amount=1000.0,
        currency="USD",
        base_rate=5.0,
        margin=2.0,
        exclude_weekends=True,
        method="simple"
    )

def test_parse_date_valid():
    date_str = "2024-12-25"
    expected_date = datetime(2024, 12, 25)
    assert parse_date(date_str) == expected_date, "parse_date should correctly parse valid date strings"

def test_parse_date_invalid_format():
    date_str = "25-12-2024"
    with pytest.raises(ValueError):
        parse_date(date_str)

def test_parse_date_nonexistent_date():
    date_str = "2024-02-30"
    with pytest.raises(ValueError):
        parse_date(date_str)

def test_simple_interest_daily_positive():
    amount = 1000.0
    annual_rate = 5.0
    expected = 1000.0 * (5.0 / 100.0) * (1/365.0)
    assert simple_interest_daily(amount, annual_rate) == expected, "simple_interest_daily should calculate correct interest"

def test_simple_interest_daily_zero_amount():
    amount = 0.0
    annual_rate = 5.0
    expected = 0.0
    assert simple_interest_daily(amount, annual_rate) == expected, "simple_interest_daily should return 0 for zero amount"

def test_simple_interest_daily_zero_rate():
    amount = 1000.0
    annual_rate = 0.0
    expected = 0.0
    assert simple_interest_daily(amount, annual_rate) == expected, "simple_interest_daily should return 0 for zero rate"

def test_simple_interest_daily_negative_amount():
    amount = -1000.0
    annual_rate = 5.0
    expected = -1000.0 * (5.0 / 100.0) * (1/365.0)
    assert simple_interest_daily(amount, annual_rate) == expected, "simple_interest_daily should handle negative amounts"

def test_simple_interest_daily_negative_rate():
    amount = 1000.0
    annual_rate = -5.0
    expected = 1000.0 * (-5.0 / 100.0) * (1/365.0)
    assert simple_interest_daily(amount, annual_rate) == expected, "simple_interest_daily should handle negative rates"


def test_daily_interest_data_simple(simple_calc):
    data = daily_interest_data(simple_calc)
    assert len(data) == 10, "There should be 9 days of interest (from Jan 1 to Jan 10)"
    first_day = data[0]
    expected_interest_no_margin = simple_interest_daily(1000.0, 5.0)
    expected_interest_with_margin = simple_interest_daily(1000.0, 7.0)
    assert first_day["Daily Interest (No Margin)"] == expected_interest_no_margin, "First day's interest without margin incorrect"
    assert first_day["Daily Interest (With Margin)"] == expected_interest_with_margin, "First day's interest with margin incorrect"
    assert first_day["Days Elapsed"] == 1, "First day's elapsed days should be 1"

def test_daily_interest_data_compound(compound_calc):
    data = daily_interest_data(compound_calc)
    assert len(data) == 10, "There should be 10 days of interest"
    first_day = data[0]
    expected_interest_no_margin = simple_interest_daily(1000.0, 5.0)
    expected_interest_with_margin = simple_interest_daily(1000.0, 7.0)
    assert first_day["Daily Interest (No Margin)"] == expected_interest_no_margin, "First day's interest without margin incorrect"
    assert first_day["Daily Interest (With Margin)"] == expected_interest_with_margin, "First day's interest with margin incorrect"
    assert first_day["Days Elapsed"] == 1, "First day's elapsed days should be 1"
    second_day = data[1]
    expected_new_amount = 1000.0 + expected_interest_with_margin
    expected_interest_with_margin_second_day = simple_interest_daily(expected_new_amount, 7.0)
    assert second_day["Daily Interest (With Margin)"] == expected_interest_with_margin_second_day, "Second day's compounded interest incorrect"

def test_daily_interest_data_exclude_weekends(exclude_weekends_calc):
    data = daily_interest_data(exclude_weekends_calc)
    assert len(data) == 8, "There should be 8 days of interest when excluding weekends"


def test_daily_interest_data_end_before_start():
    calc = CalculationData(
        start_date="2024-01-10",
        end_date="2024-01-05",
        amount=1000.0,
        currency="USD",
        base_rate=5.0,
        margin=2.0,
        exclude_weekends=False,
        method="simple"
    )
    data = daily_interest_data(calc)
    assert data == [], "No interest should be calculated when end_date is before start_date"

def test_daily_interest_data_zero_amount(simple_calc):
    calc = CalculationData(
        start_date="2024-01-01",
        end_date="2024-01-10",
        amount=0.0,
        currency="USD",
        base_rate=5.0,
        margin=2.0,
        exclude_weekends=False,
        method="simple"
    )
    data = daily_interest_data(calc)
    for day in data:
        assert day["Daily Interest (No Margin)"] == 0.0, "Interest without margin should be 0 for zero amount"
        assert day["Daily Interest (With Margin)"] == 0.0, "Interest with margin should be 0 for zero amount"

def test_daily_interest_data_invalid_method():
    calc = CalculationData(
        start_date="2024-01-01",
        end_date="2024-01-10",
        amount=1000.0,
        currency="USD",
        base_rate=5.0,
        margin=2.0,
        exclude_weekends=False,
        method="invalid_method"
    )
    with pytest.raises(ValueError, match="Unknown method: invalid_method"):
            daily_interest_data(calc)



def test_total_interest_simple(simple_calc):
    data = daily_interest_data(simple_calc)
    total = total_interest(simple_calc, with_margin=True)
    expected_total = sum(day["Daily Interest (With Margin)"] for day in data)
    assert total == expected_total

def test_total_interest_compound(compound_calc):
    data = daily_interest_data(compound_calc)
    total = total_interest(compound_calc, with_margin=True)
    expected_total = sum(day["Daily Interest (With Margin)"] for day in data)
    assert total == expected_total

def test_total_interest_no_margin(simple_calc):
    data = daily_interest_data(simple_calc)
    total = total_interest(simple_calc, with_margin=False)
    expected_total = sum(day["Daily Interest (No Margin)"] for day in data)
    assert total == expected_total

def test_total_interest_zero_days():
    calc = CalculationData(
        start_date="2024-01-10",
        end_date="2024-01-10",
        amount=1000.0,
        currency="USD",
        base_rate=5.0,
        margin=2.0,
        exclude_weekends=False,
        method="simple"
    )
    total = total_interest(calc)
    assert total == simple_interest_daily(1000.0, 7.0), "Total interest should be equal to daily interest for a single day"

def test_total_interest_negative_amount():
    calc = CalculationData(
        start_date="2024-01-01",
        end_date="2024-01-10",
        amount=-1000.0,
        currency="USD",
        base_rate=5.0,
        margin=2.0,
        exclude_weekends=False,
        method="simple"
    )
    total = total_interest(calc)
    expected_total = sum(day["Daily Interest (With Margin)"] for day in daily_interest_data(calc))
    assert total == expected_total, "total_interest should handle negative amounts correctly"

if __name__ == "__main__":
    pytest.main(["-v", "test_interest_calculations.py"])