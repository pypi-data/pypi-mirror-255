import pytest
from covalent.services.util.prettify_currency import prettify_currency

class TestPrettifyCurrency:
    """ prettify currency test class """

    def test_adding_decimals_to_integer_values(self):
        num = 89.00
        decimals = 2
        pretty_currency = prettify_currency(num, decimals, "CAD")
        assert pretty_currency == "CA$89.00"

    def test_random_string_will_default_to_0_00(self):
        decimals = 2
        pretty_currency = prettify_currency("alkjsdlaksjdlasjdlaksjdlaskjda", decimals, "USD")
        assert pretty_currency == "$0.00"

    def test_more_than_2_decimal_places(self):
        num = 812381941.0124591231341
        decimals = 5
        pretty_currency = prettify_currency(num, decimals, "NGN")
        assert pretty_currency == "₦812.38194M"

    def test_ignore_small_value_true(self):
        num = 0.000001
        decimals = 2
        pretty_currency = prettify_currency(num, decimals, "USD", True)
        assert pretty_currency == "<$0.01"

    def test_ignore_zero_true(self):
        num = 0.00
        decimals = 2
        pretty_currency = prettify_currency(num, decimals, "USD", False, True, True)
        assert pretty_currency == "<$0.01"

    def test_different_currency(self):
        num = 20.45
        decimals = 2
        pretty_currency = prettify_currency(num, decimals, "TRY")
        assert pretty_currency == "₺20.45"

    def test_negative_values(self):
        num = -45.67
        decimals = 2
        pretty_currency = prettify_currency(num, decimals, "USD")
        assert pretty_currency == "$-45.67"

    def test_negative_values_with_ignore_small_values_true(self):
        num = -45.67
        decimals = 2
        pretty_currency = prettify_currency(num, decimals, "USD", True)
        assert pretty_currency == "<$0.01"

    def test_input_integer_values(self):
        num = 6
        decimals = 2
        pretty_currency = prettify_currency(num, decimals, "USD", True)
        assert pretty_currency == "$6.00"


            