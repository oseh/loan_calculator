from typing import Dict, Any, Tuple, ItemsView
from dataclasses import dataclass

@dataclass
class CalculationData:
    start_date: str
    end_date: str
    amount: float
    currency: str
    base_rate: float
    margin: float
    exclude_weekends: bool
    method: str
    
    def __hash__(self) -> int:
        return hash((self.start_date, self.end_date, self.amount, self.currency, self.base_rate, self.margin, self.exclude_weekends, self.method))
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CalculationData):
            return False
        return self.start_date == other.start_date and self.end_date == other.end_date and self.amount == other.amount and self.currency == other.currency and self.base_rate == other.base_rate and self.margin == other.margin and self.exclude_weekends == other.exclude_weekends and self.method == other.method

calculations: Dict[int, CalculationData] = {}
next_id: int = 0

def save_calculation(caldata: CalculationData, calc_id: int = -1) -> int:
    global next_id
    calculations[calc_id if calc_id != -1 else next_id] = caldata
    next_id += 1
    current_id: int = next_id - 1
    return current_id

def get_calculation(calc_id: int) -> CalculationData:
    return calculations.get(calc_id)

def list_calculations() -> list[tuple[int, CalculationData]]:
    return list(calculations.items())
