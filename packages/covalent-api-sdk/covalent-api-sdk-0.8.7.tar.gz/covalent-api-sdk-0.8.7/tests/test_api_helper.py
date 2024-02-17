from datetime import datetime
import pytest
from covalent.services.util.api_helper import check_and_modify_response

class TestApiHelper:
    """ api helper test class """

    @pytest.fixture
    def client(self):
        class TestResponse:
            """ test class """
            address: str
            updated_at: datetime
            next_update_at: datetime
            quote_currency: str
            chain_id: int
            chain_name: str
            current_page: int

            def __init__(self, data):
                self.address = data["address"]
                self.updated_at = data["updated_at"]
                self.next_update_at = data["next_update_at"]
                self.quote_currency = data["quote_currency"]
                self.chain_id = data["chain_id"]
                self.chain_name = data["chain_name"]
                self.current_page = data["current_page"]

        test_response = {
            "address": "0xfc43f5f9dd45258b3aff31bdbe6561d97e8b71de",
            "updated_at": "2023-07-12T17:14:25.666515061Z",
            "next_update_at": "2023-07-12T17:19:25.666517561Z",
            "quote_currency": "USD",
            "chain_id": 1,
            "chain_name": "eth-mainnet",
            "current_page": 10,
        }

        return TestResponse(test_response)

    def test_remove_field(self, client):
        """ test to see if mock response is the same as actual response """
        check_and_modify_response(vars(client))
        assert "next_update_at" not in list(vars(client).keys())
