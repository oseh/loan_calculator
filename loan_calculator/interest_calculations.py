from datetime import datetime, timedelta
from typing import List, Dict, Callable
from loan_calculator.data_store import CalculationData
from functools import lru_cache  

def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")

def is_weekend(day: datetime) -> bool:
    return day.weekday() >= 5 

def simple_interest_daily(amount: float, annual_rate: float) -> float:
    return amount * (annual_rate / 100.0) * (1/365.0)

@lru_cache(maxsize=None)
def daily_interest_data(
    calc_data: CalculationData 
) -> List[Dict[str, str | float]]:
    start = parse_date(calc_data.start_date)
    end = parse_date(calc_data.end_date)
    total_days = (end - start).days + 1
    if total_days < 1:
        return []

    results: List[Dict[str, str | float]] = []
    days_counted = 0
    current_amount = calc_data.amount 
    for i in range(0, total_days):
        accrual_date = start + timedelta(days=i)
        if calc_data.exclude_weekends and is_weekend(accrual_date):
            continue
        days_counted += 1

        if calc_data.method == "compound":
            daily_base = simple_interest_daily(current_amount, calc_data.base_rate)
            daily_total = simple_interest_daily(current_amount, calc_data.base_rate + calc_data.margin)
            current_amount += daily_total
        elif calc_data.method == "simple":
            daily_base = simple_interest_daily(calc_data.amount, calc_data.base_rate)
            daily_total = simple_interest_daily(calc_data.amount, calc_data.base_rate + calc_data.margin)
        else:
            raise ValueError(f"Unknown method: {calc_data.method}")

        results.append({
            "Accrual Date": accrual_date.strftime("%Y-%m-%d"),
            "Daily Interest (No Margin)": daily_base,
            "Daily Interest (With Margin)": daily_total,
            "Days Elapsed": days_counted
        })
    return results

@lru_cache(maxsize=None)
def total_interest(
    calc_data: CalculationData, with_margin: bool = True
) -> float:
    data = daily_interest_data(calc_data)
    if with_margin:
        return sum(d["Daily Interest (With Margin)"] for d in data)
    return sum(d["Daily Interest (No Margin)"] for d in data)
