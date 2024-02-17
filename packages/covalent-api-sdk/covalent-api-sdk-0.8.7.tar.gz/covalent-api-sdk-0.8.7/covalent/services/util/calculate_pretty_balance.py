from decimal import Decimal, getcontext

def calculate_pretty_balance(value, decimals=18, round_off=True, precision=0):
    getcontext().prec = 50  # Setting precision for the decimal module

    if isinstance(value, (float, Decimal)):
        big_decimal_value = Decimal(str(value))
    elif isinstance(value, int):
        big_int_value = int(value)
        big_decimal_value = Decimal(str(big_int_value))
    else:
        return -1

    _decimals = decimals or 18
    _expo_value = 10 ** _decimals
    big_decimal_expo = Decimal(str(_expo_value))
    _calculated = big_decimal_value / big_decimal_expo

    # Removes the decimal places, true by default so it adds decimals
    if not round_off:
        return str(_calculated)

    _decimal_fixed = precision
    if precision == 0:
        _decimal_fixed = 2
        if _calculated < 100:
            _decimal_fixed = 6

    return format(_calculated, f".{_decimal_fixed}f")