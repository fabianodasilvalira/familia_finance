from typing import Tuple

def get_transaction_color(transaction_type: str) -> str:
    """Return color class based on transaction type"""
    if transaction_type == "income":
        return "text-green-600"
    elif transaction_type == "expense":
        return "text-red-600"
    return "text-gray-600"

def get_progress_color(percentage: float) -> str:
    """Return color class based on percentage"""
    if percentage < 0.3:
        return "bg-red-500"
    elif percentage < 0.7:
        return "bg-yellow-500"
    else:
        return "bg-green-500"

def get_budget_status_color(percentage: float) -> str:
    """Return color class based on budget usage percentage"""
    if percentage >= 0.9:
        return "text-red-600"
    elif percentage >= 0.7:
        return "text-yellow-600"
    else:
        return "text-green-600"
