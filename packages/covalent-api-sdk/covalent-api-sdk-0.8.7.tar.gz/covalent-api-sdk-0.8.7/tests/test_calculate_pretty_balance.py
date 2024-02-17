import pytest
from covalent.services.util.calculate_pretty_balance import calculate_pretty_balance

class TestCalculatePrettyBalance:
    """ calculate pretty balance test class """

    def test_round_off_no_specified_precision(self):
        num: int = 10123581891238191295
        decimals: int = 18
        unscaled_balance = calculate_pretty_balance(num, decimals)
        assert unscaled_balance == "10.123582"
    
    def test_without_round_off_no_specified_precision(self):
        num: int = 8483983120120315234234
        decimals: int = 18
        unscaled_balance = calculate_pretty_balance(num, decimals, False)
        assert unscaled_balance == "8483.983120120315234234"
    
    def test_round_off_specified_precision(self):
        num: int = 2301235481943895082304981091058190283091283901
        decimals: int = 18
        unscaled_balance = calculate_pretty_balance(num, decimals, True, 4)
        assert unscaled_balance == "2301235481943895082304981091.0582"
    
    def test_error_handling(self):
        decimals: int = 18
        unscaled_balance = calculate_pretty_balance("testing", decimals, True, 4)
        assert unscaled_balance == -1
    
    def test_decimal_value(self):
        num = 1.5000000
        decimals: int = 3
        unscaled_balance = calculate_pretty_balance(num, decimals, True, 4)
        assert unscaled_balance == "0.0015"
        