import pytest
import os
from covalent import CovalentClient
from covalent.services.util.chains import Chains


class TestBalanceService:
    """ balance service testing class """

    @pytest.fixture
    def client(self):
        """ initialize client """
        return CovalentClient(os.environ.get('COVALENT_API_KEY'))

    # token balance endpoint testing
    def test_token_balance_nft_success(self, client: CovalentClient):
        """ test for token balance endpoint with nft enabled success """
        tok_bal_nft = client.balance_service.get_token_balances_for_wallet_address(Chains.ETH_MAINNET, "demo.eth", "CAD", True)
        assert tok_bal_nft.error is False
        assert tok_bal_nft.data.chain_id == 1
        assert tok_bal_nft.data.chain_name == "eth-mainnet"
        assert tok_bal_nft.data.quote_currency == "CAD"
        assert len(tok_bal_nft.data.items) > 0
        assert tok_bal_nft.data.items[124].nft_data is not None

    def test_token_balance_nft_false_success(self, client: CovalentClient):
        """ test for token balance endpoint with nft disabled success """
        tok_bal_nft_false = client.balance_service.get_token_balances_for_wallet_address(Chains.ETH_MAINNET, "demo.eth", "CAD", False)
        assert tok_bal_nft_false.error is False
        assert tok_bal_nft_false.data.chain_id == 1
        assert tok_bal_nft_false.data.chain_name == "eth-mainnet"
        assert tok_bal_nft_false.data.quote_currency == "CAD"
        assert len(tok_bal_nft_false.data.items) > 0
        assert tok_bal_nft_false.data.items[0].nft_data is None

    def test_token_balance_fail(self, client: CovalentClient):
        """ test for token balance endpoint fail """
        tok_bal_fail = client.balance_service.get_token_balances_for_wallet_address("eth-mainnet", "demo.ethhh")
        assert tok_bal_fail.error is True

    # historical token balance endpoint testing
    def test_historical_token_balance_success(self, client: CovalentClient):
        """ test for historical token balance endpoint success """
        hist_tok_bal = client.balance_service.get_historical_token_balances_for_wallet_address("eth-mainnet", "demo.eth", "AUD")
        assert hist_tok_bal.error is False
        assert hist_tok_bal.data.chain_id == 1
        assert hist_tok_bal.data.chain_name == "eth-mainnet"
        assert hist_tok_bal.data.quote_currency == "AUD"
        assert len(hist_tok_bal.data.items) > 0

    def test_historical_token_balance_fail(self, client: CovalentClient):
        """ test for historical token balance endpoint fail """
        hist_tok_bal_fail = client.balance_service.get_historical_token_balances_for_wallet_address(Chains.ETH_MAINNET, "demo.ethhh", "AUD")
        assert hist_tok_bal_fail.error is True

    # historical portfolio endpoint testing
    def test_historical_portfolio_success(self, client: CovalentClient):
        """ test for historical portfolio endpoint success """
        hist_port_7 = client.balance_service.get_historical_portfolio_for_wallet_address(Chains.ETH_MAINNET, "demo.eth", "AUD", 7)
        assert hist_port_7.error is False
        assert hist_port_7.data.chain_id == 1
        assert hist_port_7.data.chain_name == "eth-mainnet"
        assert hist_port_7.data.quote_currency == "AUD"
        assert len(hist_port_7.data.items) > 0
        assert len(hist_port_7.data.items[0].holdings) == 8

    def test_historical_portfolio_fail(self, client: CovalentClient):
        """ test for historical portfolio endpoint fail """
        hist_port_7_fail = client.balance_service.get_historical_portfolio_for_wallet_address("eth-mainnet", "demo.eth", "AUD", -1)
        assert hist_port_7_fail.error is True

    # erc20 endpoint testing
    @pytest.mark.asyncio
    async def test_erc20_transfer_endpoint_success(self, client: CovalentClient):
        """ test for erc20 transfers endpoint success """
        async for res in client.balance_service.get_erc20_transfers_for_wallet_address(Chains.ETH_MAINNET, "demo.eth", "USD", "0xdac17f958d2ee523a2206206994597c13d831ec7"):
            assert res is not None

    @pytest.mark.asyncio
    async def test_erc20_transfer_endpoint_fail(self, client: CovalentClient):
        """ test for erc20 transfers endpoint fail """
        with pytest.raises(Exception) as exc_info:
            async for res in client.balance_service.get_erc20_transfers_for_wallet_address("eth-mainnet", "demo.eth", "USD", "0xdac17f958d2ee"):
                assert "An error occured 400 : Malformed address provided: 0xdac17f958d2ee" in str(exc_info.value)
        
    # token holders v2 endpoint testing
    @pytest.mark.asyncio
    async def test_token_holders_v2_endpoint_success(self, client: CovalentClient):
        """ test for token holders v2 endpoint success """
        async for res in client.balance_service.get_token_holders_v2_for_token_address("eth-mainnet", "0x987d7cc04652710b74fff380403f5c02f82e290a"):
            assert res is not None
    
    @pytest.mark.asyncio
    async def test_token_holders_v2_endpoint_fail(self, client: CovalentClient):
        """ test for token holders v2 endpoint fail """
        with pytest.raises(Exception) as exc_info:
            async for res in client.balance_service.get_token_holders_v2_for_token_address("eth-mainnet", "0x987d7cc04652710b74fff380403f5c"):
                assert "An error occured 400 : Malformed address provided: 0x987d7cc04652710b74fff380403f5c" in str(exc_info.value)

    # native token balance endpoint testing
    def test_native_token_balance_success(self, client: CovalentClient):
        """ test for native token balance endpoint success """
        native_token = client.balance_service.get_native_token_balance(Chains.ETH_MAINNET, "demo.eth", "AUD")
        assert native_token.error is False
        assert native_token.data.chain_id == 1
        assert native_token.data.chain_name == "eth-mainnet"
        assert native_token.data.quote_currency == "AUD"
        assert len(native_token.data.items) > 0

    def test_native_token_balance_fail(self, client: CovalentClient):
        """ test for native_token_balance endpoint fail """
        native_token_balance_fail = client.balance_service.get_native_token_balance("eth-mainnet", "demo")
        assert native_token_balance_fail.error is True
        
    def test_erc20_token_transfer_by_page_success(self, client: CovalentClient):
        """ test for erc20 token transfer by page endpoint success """
        erc20 = client.balance_service.get_erc20_transfers_for_wallet_address_by_page("eth-mainnet", "demo.eth", "AUD", "0xdac17f958d2ee523a2206206994597c13d831ec7")
        assert erc20.error is False
        assert erc20.data.chain_id == 1
        assert erc20.data.chain_name == "eth-mainnet"
        assert erc20.data.quote_currency == "AUD"
        assert len(erc20.data.items) > 0

    def test_erc20_token_transfer_by_page_fail(self, client: CovalentClient):
        """ test for erc20 token transfer by page endpoint fail """
        native_token_balance_fail = client.balance_service.get_erc20_transfers_for_wallet_address_by_page(Chains.ETH_MAINNET, "demo")
        assert native_token_balance_fail.error is True

    def test_get_token_holders_v2_by_page_success(self, client: CovalentClient):
        """ test for token holders by page endpoint success """
        tokenHoldersbyPage = client.balance_service.get_token_holders_v2_for_token_address_by_page("eth-mainnet", "0x987d7cc04652710b74fff380403f5c02f82e290a")
        assert tokenHoldersbyPage.error is False
        assert tokenHoldersbyPage.data.chain_id == 1
        assert tokenHoldersbyPage.data.chain_name == "eth-mainnet"
        assert len(tokenHoldersbyPage.data.items) > 0
    
    def test_get_token_holders_v2_by_page_fail(self, client: CovalentClient):
        """ test for token holders by page endpoint fail """
        tokenHoldersbyPage = client.balance_service.get_token_holders_v2_for_token_address_by_page(Chains.ETH_MAINNET, "0x987d7cc04652710b74fff380403f5c02f82e")
        assert tokenHoldersbyPage.error is True