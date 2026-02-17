def format_thai_amount(amount: float) -> str:
    if amount is None:
        return ""
    is_negative = amount < 0
    abs_amount = abs(amount)
    if abs_amount < 1_000_000:
        formatted = f"{abs_amount:,.0f}"
        return f"-{formatted}" if is_negative else formatted

    value = abs_amount
    unit_suffix = ""
    
    while value >= 1_000_000:
        value /= 1_000_000
        unit_suffix += "ล้าน"
        
    if value % 1 == 0:  
        formatted = f"{value:,.0f}"
    else:
        # Show up to 2 decimal places, remove trailing zeros
        formatted = f"{value:,.2f}".rstrip('0').rstrip('.')
    
    result = f"{formatted} {unit_suffix}"
    return f"-{result}" if is_negative else result

