import pytest
import os
from covalent import CovalentClient
from covalent.services.util.chains import Chains


class TestSecurityService:
    """ security service testing class """

    @pytest.fixture
    def client(self):
        """ initialize client """
        return CovalentClient(os.environ.get('COVALENT_API_KEY'))

    def test_get_approvals_success(self, client: CovalentClient):
        """ test for approvals endpoint success """
        get_appr = client.security_service.get_approvals(Chains.ETH_MAINNET, "demo.eth")
        assert get_appr.error is False
        assert get_appr.data.chain_id == 1
        assert get_appr.data.chain_name == "eth-mainnet"
        assert len(get_appr.data.items) > 0

    def test_get_approvals_fail(self, client: CovalentClient):
        """ test for approvals endpoint fail """
        fail_appr = client.security_service.get_approvals(Chains.ETH_MAINNET, "demo.ethhh")
        assert fail_appr.error is True
        
    def test_get_nft_approvals_success(self, client: CovalentClient):
        """ test for nft approvals endpoint success """
        get_appr = client.security_service.get_nft_approvals("eth-mainnet", "0x760ff9A631a006111Cb024F6acA8977331DB260d")
        assert get_appr.error is False
        assert get_appr.data.chain_id == 1
        assert get_appr.data.chain_name == "eth-mainnet"
        assert len(get_appr.data.items) > 0
    
    def test_get_nft_approvals_fail(self, client: CovalentClient):
        """ test for nft approvals endpoint success """
        fail_appr = client.security_service.get_nft_approvals(Chains.ETH_MAINNET, "0x123")
        assert fail_appr.error is True