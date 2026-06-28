def format_currency(value: float) -> str:
    """Format value to BRL currency."""
    if value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_number(value: int) -> str:
    """Format large numbers to readable strings (e.g., 1.2k, 1M)."""
    if value is None:
        return "0"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M".replace(".", ",")
    elif value >= 1_000:
        return f"{value / 1_000:.1f}k".replace(".", ",")
    return str(value)

def format_percent(value: float) -> str:
    """Format percentage values."""
    if value is None:
        return "0.0%"
    return f"{value:,.1f}%".replace(".", ",")
