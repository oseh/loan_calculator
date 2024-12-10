import pytest
from loan_calculator.data_store import (
    CalculationData,
    save_calculation,
    get_calculation,
    list_calculations,
    calculations,
    next_id
)
from dataclasses import asdict

@pytest.fixture(autouse=True)
def reset_data_store():
    """
    Fixture to reset the in-memory data store before each test.
    Ensures test isolation and prevents state leakage.
    """
    calculations.clear()
    global next_id
    next_id = 0
    yield

def test_save_calculation_new():
    """
    Test saving a new calculation without providing a calc_id.
    Ensures that the calculation is saved with the correct ID.
    """
    calc_data = CalculationData(
        start_date="2024-01-01",
        end_date="2024-12-31",
        amount=10000.0,
        currency="USD",
        base_rate=5.0,
        margin=2.0,
        exclude_weekends=False,
        method="simple"
    )
    calc_id = save_calculation(calc_data)
    assert calc_id == 0, "First calculation ID should be 0"
    assert calculations[calc_id] == calc_data, "Saved calculation should match input data"

def test_save_calculation_with_id():
    """
    Test saving a calculation with a specific calc_id.
    Ensures that the calculation is saved with the provided ID.
    """
    calc_data = CalculationData(
        start_date="2024-02-01",
        end_date="2024-11-30",
        amount=5000.0,
        currency="EUR",
        base_rate=4.5,
        margin=1.5,
        exclude_weekends=True,
        method="compound"
    )
    calc_id = 10
    returned_id = save_calculation(calc_data, calc_id=calc_id)
    assert returned_id == calc_id, "Returned ID should match the provided calc_id"
    assert calculations[calc_id] == calc_data, "Saved calculation should match input data"

def test_save_calculation_overwrite():
    """
    Test saving a calculation with an existing calc_id.
    Ensures that the existing calculation is overwritten.
    """
    original_calc = CalculationData(
        start_date="2024-03-01",
        end_date="2024-09-30",
        amount=7500.0,
        currency="GBP",
        base_rate=4.0,
        margin=2.0,
        exclude_weekends=False,
        method="simple"
    )
    calc_id = save_calculation(original_calc)
    
    updated_calc = CalculationData(
        start_date="2024-03-15",
        end_date="2024-10-15",
        amount=8000.0,
        currency="GBP",
        base_rate=4.2,
        margin=2.1,
        exclude_weekends=True,
        method="compound"
    )
    returned_id = save_calculation(updated_calc, calc_id=calc_id)
    assert returned_id == calc_id, "Returned ID should match the provided calc_id"
    assert calculations[calc_id] == updated_calc, "Calculation should be updated with new data"

def test_get_calculation_existing():
    """
    Test retrieving an existing calculation by ID.
    """
    calc_data = CalculationData(
        start_date="2024-04-01",
        end_date="2024-10-31",
        amount=12000.0,
        currency="JPY",
        base_rate=3.5,
        margin=1.0,
        exclude_weekends=False,
        method="compound"
    )
    calc_id = save_calculation(calc_data)
    retrieved_calc = get_calculation(calc_id)
    assert retrieved_calc == calc_data, "Retrieved calculation should match the saved data"

def test_get_calculation_non_existing():
    """
    Test retrieving a calculation with a non-existing ID.
    Should return None.
    """
    retrieved_calc = get_calculation(999)
    assert retrieved_calc is None, "Retrieving non-existing calculation should return None"

def test_list_calculations_empty():
    """
    Test listing calculations when no calculations have been saved.
    Should return an empty list.
    """
    calcs = list_calculations()
    assert calcs == [], "Listing calculations should return an empty list when no calculations are saved"

def test_list_calculations_multiple():
    """
    Test listing multiple saved calculations.
    """
    calc1 = CalculationData(
        start_date="2024-05-01",
        end_date="2024-11-30",
        amount=9000.0,
        currency="CAD",
        base_rate=4.0,
        margin=1.5,
        exclude_weekends=True,
        method="simple"
    )
    calc2 = CalculationData(
        start_date="2024-06-01",
        end_date="2024-12-31",
        amount=11000.0,
        currency="AUD",
        base_rate=4.5,
        margin=2.0,
        exclude_weekends=False,
        method="compound"
    )
    id1 = save_calculation(calc1)
    id2 = save_calculation(calc2)
    
    calcs = list_calculations()
    assert len(calcs) == 2, "There should be two calculations saved"
    assert (id1, calc1) in calcs, "First calculation should be in the list"
    assert (id2, calc2) in calcs, "Second calculation should be in the list"

def test_save_calculation_invalid_id():
    """
    Test saving a calculation with an invalid calc_id (e.g., negative number).
    Depending on design, this could either allow negative IDs or raise an error.
    Here, we assume negative IDs are allowed as per the current implementation.
    """
    calc_data = CalculationData(
        start_date="2024-07-01",
        end_date="2024-12-31",
        amount=6000.0,
        currency="CHF",
        base_rate=3.8,
        margin=1.2,
        exclude_weekends=True,
        method="simple"
    )
    calc_id = -5
    returned_id = save_calculation(calc_data, calc_id=calc_id)
    assert returned_id == calc_id, "Returned ID should match the provided negative calc_id"
    assert calculations[calc_id] == calc_data, "Calculation should be saved with the negative calc_id"

def test_save_calculation_duplicate():
    """
    Test saving two different calculations with the same calc_id.
    The second save should overwrite the first one.
    """
    calc1 = CalculationData(
        start_date="2024-08-01",
        end_date="2024-12-15",
        amount=7000.0,
        currency="NZD",
        base_rate=4.2,
        margin=1.8,
        exclude_weekends=False,
        method="compound"
    )
    calc2 = CalculationData(
        start_date="2024-08-15",
        end_date="2024-12-31",
        amount=7500.0,
        currency="NZD",
        base_rate=4.3,
        margin=1.9,
        exclude_weekends=True,
        method="simple"
    )
    calc_id = save_calculation(calc1)
    returned_id = save_calculation(calc2, calc_id=calc_id)
    
    assert returned_id == calc_id, "Returned ID should match the provided calc_id"
    assert calculations[calc_id] == calc2, "Second calculation should overwrite the first one"

def test_calculation_data_equality():
    """
    Test the equality of two CalculationData instances.
    """
    calc1 = CalculationData(
        start_date="2024-11-01",
        end_date="2025-04-30",
        amount=8500.0,
        currency="SGD",
        base_rate=4.0,
        margin=1.5,
        exclude_weekends=True,
        method="simple"
    )
    calc2 = CalculationData(
        start_date="2024-11-01",
        end_date="2025-04-30",
        amount=8500.0,
        currency="SGD",
        base_rate=4.0,
        margin=1.5,
        exclude_weekends=True,
        method="simple"
    )
    calc3 = CalculationData(
        start_date="2024-11-15",
        end_date="2025-05-15",
        amount=9000.0,
        currency="SGD",
        base_rate=4.1,
        margin=1.6,
        exclude_weekends=False,
        method="compound"
    )
    assert calc1 == calc2, "Identical CalculationData instances should be equal"
    assert calc1 != calc3, "Different CalculationData instances should not be equal"

def test_calculation_data_hash():
    """
    Test the hashing of CalculationData instances.
    Ensures that identical instances have the same hash and can be used in sets/dicts.
    """
    calc1 = CalculationData(
        start_date="2024-12-01",
        end_date="2025-06-30",
        amount=9500.0,
        currency="CHF",
        base_rate=3.9,
        margin=1.3,
        exclude_weekends=False,
        method="compound"
    )
    calc2 = CalculationData(
        start_date="2024-12-01",
        end_date="2025-06-30",
        amount=9500.0,
        currency="CHF",
        base_rate=3.9,
        margin=1.3,
        exclude_weekends=False,
        method="compound"
    )
    calc_set = {calc1, calc2}
    assert len(calc_set) == 1, "Identical CalculationData instances should have the same hash and be treated as one in a set"

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_data_store.py"])