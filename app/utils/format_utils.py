def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:.2f}"

def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value * 100:.1f}%"
