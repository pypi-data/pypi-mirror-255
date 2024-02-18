from enum import Enum


class BillingMethod(str, Enum):
    BUDGET_NUMBER = "BUDGET_NUMBER"
    CREDIT = "CREDIT"
    PURCHASE_ORDER = "PURCHASE_ORDER"

    def __str__(self) -> str:
        return str(self.value)
