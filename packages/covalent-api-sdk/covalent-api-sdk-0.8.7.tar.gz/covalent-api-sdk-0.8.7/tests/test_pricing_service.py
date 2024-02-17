from covalent import CovalentClient
import pytest
import os

from covalent.services.util.chains import Chains



class TestPricingService:
    
    @pytest.fixture
    def client(self):
        return CovalentClient(os.environ.get('COVALENT_API_KEY'))

    def test_success(self, client: CovalentClient):
        res = client.pricing_service.get_token_prices(Chains.ETH_MAINNET, "CAD", "0x39ee2c7b3cb80254225884ca001f57118c8f21b6")
        assert res.data[0].contract_name == "Potatoz"
        assert res.data[0].contract_address == "0x39ee2c7b3cb80254225884ca001f57118c8f21b6"
        assert res.data[0].quote_currency == "CAD"
        
    def test_different_quote_currencies(self, client: CovalentClient):
        res = client.pricing_service.get_token_prices(Chains.ETH_MAINNET, "EUR", "0xb8c77482e45f1f44de1745f52c74426c631bdd52")
        assert res.data[0].contract_name == "BNB"
        assert res.data[0].contract_address == "0xb8c77482e45f1f44de1745f52c74426c631bdd52"
        assert res.data[0].quote_currency == "EUR"
        
    def test_incorrect_contract_address(self, client: CovalentClient):
        res = client.pricing_service.get_token_prices("eth-mainnet", "EUR", "0x123")
        assert res.error is True
        assert res.error_code == 400
        assert res.error_message == "Malformed address provided: 0x123"
