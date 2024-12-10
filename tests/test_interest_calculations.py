import pytest
from loan_calculator.interest_calculations import (
    daily_interest_data,
    total_interest,
    simple_interest_daily
)

def test_simple_interest_daily():
    result = simple_interest_daily(10000, 5)
    assert pytest.approx(result, 0.001) == 10000 * 0.05 / 365

def test_daily_interest_data_basic():
    data = daily_interest_data(
        start_date="2024-01-01",
        end_date="2024-01-03",
        amount=10000,
        base_rate=5,
        margin=2,
        exclude_weekends=False,
        method="simple"
    )
    assert len(data) == 2
    assert data[0]["Days Elapsed"] == 1
    assert data[1]["Days Elapsed"] == 2

def test_total_interest():
    total = total_interest(
        start_date="2024-01-01",
        end_date="2024-01-11",
        amount=10000,
        base_rate=5,
        margin=2,
        exclude_weekends=False,
        method="simple"
    )
    daily = 10000 * 0.07 / 365
    expected_total = daily * 10
    assert pytest.approx(total, 0.0001) == expected_total
