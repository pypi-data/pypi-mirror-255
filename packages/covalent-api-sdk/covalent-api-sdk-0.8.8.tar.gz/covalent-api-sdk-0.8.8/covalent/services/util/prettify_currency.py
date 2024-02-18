from typing import Union
import math
from .types import quote

LESS_THAN_ZERO = "0.01"
ZERO = "0.00"

currency_map = {
    "USD": "$",
    "CAD": "CA$",
    "EUR": "€",
    "SGD": "S$",
    "INR": "₹",
    "JPY": "¥",
    "VND": "₫",
    "CNY": "CN¥",
    "KRW": "₩",
    "RUB": "₽",
    "TRY": "₺",
    "NGN": "₦",
    "ARS": "ARS",
    "AUD": "A$",
    "CHF": "CHF",
    "GBP": "£"
}

def prettify_currency(value: Union[str, float], decimals: int = 2, currency: quote = "USD", ignore_small_value: bool = False, ignore_minus: bool = True, ignore_zero: bool = False):
    
    try:
        value = float(value)
    except ValueError as e:
        return currency_map.get(currency, '$') + ZERO

    minus = ""
    currency_suffix = ""
    # pass ignore_minus False to get the negative number for currency formatter
    if not ignore_minus and value < 0:
        value = abs(value)
        minus = "-"

    if value == 0 or not value:
        # if value is 0, pass ignore_zero True to get this string "<$0.01"
        if ignore_zero:
            return f"<{currency_map.get(currency, '$')}{LESS_THAN_ZERO}"
        else:
            return currency_map.get(currency, '$') + ZERO
    elif value < 0 or value < 1:
        if value < 0.01 and ignore_small_value:
            return f"<{currency_map.get(currency, '$')}{LESS_THAN_ZERO}"
    elif value > 999999999:
        value /= 1000000000
        currency_suffix = "B"
    elif value > 999999:
        value /= 1000000  # convert to M for number from > 1 million
        currency_suffix = "M"

    # Added to round down the number
    expo = 10 ** decimals
    value = math.floor(value * expo) / expo

    # generates the value with the inputted currency
    formatter = "{:,.{}f}".format(value, decimals)
    currency_symbol = currency_map.get(currency, "$")
    formatted_value = f"{currency_symbol}{formatter}"
    
    return f"{minus}{formatted_value}{currency_suffix}"