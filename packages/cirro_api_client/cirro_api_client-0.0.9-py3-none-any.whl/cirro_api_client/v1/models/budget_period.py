from enum import Enum


class BudgetPeriod(str, Enum):
    ANNUALLY = "ANNUALLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"

    def __str__(self) -> str:
        return str(self.value)
