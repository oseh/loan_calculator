from loan_calculator.data_store import save_calculation, get_calculation, list_calculations

def test_save_and_get_calculation():
    calc_id = save_calculation({
        "start_date": "2024-01-01",
        "end_date": "2024-01-10",
        "amount": 10000,
        "currency": "USD",
        "base_rate": 5,
        "margin": 2,
        "exclude_weekends": False,
        "method": "simple"
    })
    assert calc_id == 1
    calc = get_calculation(calc_id)
    assert calc is not None
    assert calc["currency"] == "USD"

def test_list_calculations():
    calcs = list(list_calculations())
    assert len(calcs) >= 1
    cid, calc = calcs[0]
    assert calc["amount"] == 10000

if __name__ == "__main__":
    test_save_and_get_calculation()
    test_list_calculations()