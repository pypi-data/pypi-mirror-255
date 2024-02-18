from covalent import CovalentClient
import pytest
import os

from covalent.services.util.chains import Chains



class TestXykService:
    
    @pytest.fixture
    def client(self):
        return CovalentClient(os.environ.get('COVALENT_API_KEY'))

    def test_get_pools_success(self, client: CovalentClient):
        pools = client.xyk_service.get_pools("fantom-mainnet", "spiritswap", "2024-01-01")

        assert not pools.error
        assert pools.data.chain_id == 250
        assert pools.data.chain_name == "fantom-mainnet"
        assert len(pools.data.items) > 0

    def test_get_pools_error(self, client: CovalentClient):
        pools_error = client.xyk_service.get_pools(Chains.FANTOM_MAINNET, "uniswap_v3", "2024-01-011")

        assert pools_error.error

    def test_get_pool_by_address_success(self, client: CovalentClient):
        pools_address = client.xyk_service.get_pool_by_address("fantom-mainnet", "spiritswap", "0xdbc490b47508d31c9ec44afb6e132ad01c61a02c")

        assert not pools_address.error
        assert pools_address.data.chain_id == 250
        assert pools_address.data.chain_name == "fantom-mainnet"
        assert len(pools_address.data.items) > 0

    def test_get_pool_by_address_error(self, client: CovalentClient):
        pools_address_error = client.xyk_service.get_pool_by_address(Chains.FANTOM_MAINNET, "uniswap_v2", "0xdbc490b47508d31c9ec44afb6e132ad01c61a02c")
        
        assert pools_address_error.error
        
    def test_get_pool_for_token_address_success(self, client: CovalentClient):
        pools_token_address = client.xyk_service.get_pools_for_token_address(Chains.ETH_MAINNET, "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", 0)

        assert not pools_token_address.error
        assert pools_token_address.data.chain_id == 1
        assert pools_token_address.data.chain_name == "eth-mainnet"
        assert len(pools_token_address.data.items) > 0

    def test_get_pool_for_token_address_error(self, client: CovalentClient):
        pools_token_address_error = client.xyk_service.get_pools_for_token_address("eth-mainnet", "testWallet", 0)
        
        assert pools_token_address_error.error
    
    def test_address_exchange_balances_success(self, client: CovalentClient):
        res = client.xyk_service.get_address_exchange_balances(Chains.ETH_MAINNET, "uniswap_v2", "demo.eth")

        assert res.error is False
        assert res.data.chain_id == 1
        assert res.data.chain_name == "eth-mainnet"
        assert len(res.data.items) > 0
        
    def test_address_exchange_balances_error(self, client: CovalentClient):
        res = client.xyk_service.get_address_exchange_balances("eth-mainnet", "uniswap_v3", "demo.eth")

        assert res.error is True
    
    def test_network_exchange_token_success(self, client: CovalentClient):
        res = client.xyk_service.get_network_exchange_tokens("fantom-mainnet", "spiritswap")

        assert res.error is False
        assert res.data.chain_id == 250
        assert res.data.chain_name == "fantom-mainnet"
    
    def test_network_exchange_token_error(self, client: CovalentClient):
        res = client.xyk_service.get_network_exchange_tokens("fantom-mainnet", "uniswap_v3")

        assert res.error is True
    
    def test_supported_dexes_success(self, client: CovalentClient):
        res = client.xyk_service.get_supported_dexes()

        assert res.error is False
        assert len(res.data.items) > 0
        assert res.data.items[0].dex_name == "uniswap_v2"
        
    def test_dex_for_pool_success(self, client: CovalentClient):
        res = client.xyk_service.get_dex_for_pool_address(Chains.ETH_MAINNET, "0x21b8065d10f73ee2e260e5b47d3344d3ced7596e")

        assert res.error is False
        assert len(res.data.items) > 0
        assert res.data.items[0].dex_name == "uniswap_v2"

    def test_signal_network_exchange_token_success(self, client: CovalentClient):
        res = client.xyk_service.get_single_network_exchange_token("eth-mainnet", "uniswap_v2", "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")

        assert res.error is False
        assert len(res.data.items) > 0
        assert res.data.chain_id == 1
        assert res.data.chain_name == "eth-mainnet"
        assert res.data.items[0].dex_name == "uniswap_v2"
        
    def test_single_network_exchange_token_success(self, client: CovalentClient):
        res = client.xyk_service.get_single_network_exchange_token("eth-mainnet", "uniswap_v2", "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")

        assert res.error is False
        assert len(res.data.items) > 0
        assert res.data.chain_id == 1
        assert res.data.chain_name == "eth-mainnet"
        assert res.data.items[0].dex_name == "uniswap_v2"
    
    def test_single_network_exchange_token_error(self, client: CovalentClient):
        res = client.xyk_service.get_single_network_exchange_token(Chains.ETH_MAINNET, "uniswap_v3", "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")

        assert res.error is True
    
    def test_transactions_for_account_address_success(self, client: CovalentClient):
        res = client.xyk_service.get_transactions_for_account_address("eth-mainnet", "uniswap_v2", "demo.eth")

        assert res.error is False
        assert res.data.chain_id == 1
        assert res.data.chain_name == "eth-mainnet"
        assert len(res.data.items) > 0
    
    def test_transactions_for_account_address_error(self, client: CovalentClient):
        res = client.xyk_service.get_transactions_for_account_address("eth-mainnet", "uniswap_v3", "demo.eth")

        assert res.error is True
    
    def test_transactions_for_token_address_success(self, client: CovalentClient):
        res = client.xyk_service.get_transactions_for_token_address(Chains.ETH_MAINNET, "uniswap_v2", "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")

        assert res.error is False
        assert res.data.chain_id == 1
        assert res.data.chain_name == "eth-mainnet"
        assert len(res.data.items) > 0
    
    def test_transactions_for_token_address_error(self, client: CovalentClient):
        res = client.xyk_service.get_transactions_for_token_address("eth-mainnet", "uniswap_v3", "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")

        assert res.error is True

    def test_transactions_for_exchange_success(self, client: CovalentClient):
        res = client.xyk_service.get_transactions_for_exchange(Chains.FANTOM_MAINNET, "spiritswap", "0xdbc490b47508d31c9ec44afb6e132ad01c61a02c")

        assert res.error is False
        assert res.data.chain_id == 250
        assert res.data.chain_name == "fantom-mainnet"
        assert len(res.data.items) > 0
    
    def test_transactions_for_exchange_error(self, client: CovalentClient):
        res = client.xyk_service.get_transactions_for_exchange("fantom-mainnet", "uniswap_v2", "0xdbc490b47508d31c9ec44afb6e132ad01c61a02c")

        assert res.error is True
        
    def test_ecosystem_chart_data_success(self, client: CovalentClient):
        res = client.xyk_service.get_ecosystem_chart_data(Chains.FANTOM_MAINNET, "spiritswap")

        assert res.error is False
        assert res.data.chain_id == 250
        assert res.data.chain_name == "fantom-mainnet"
        assert len(res.data.items) > 0
        
    def test_ecosystem_chart_data_error(self, client: CovalentClient):
        res = client.xyk_service.get_ecosystem_chart_data("fantom-mainnet", "uniswap_v3")

        assert res.error is True
        
    def test_health_data_success(self, client: CovalentClient):
        res = client.xyk_service.get_health_data(Chains.ETH_MAINNET, "uniswap_v2")

        assert res.error is False
        assert res.data.chain_id == 1
        assert res.data.chain_name == "eth-mainnet"
        assert len(res.data.items) > 0
    
    def test_health_data_error(self, client: CovalentClient):
        res = client.xyk_service.get_health_data("eth-mainnet", "uniswap_v3")

        assert res.error is True
    
    def test_get_lp_token_view_success(self, client: CovalentClient):
        res = client.xyk_service.get_lp_token_view(Chains.ETH_MAINNET, "uniswap_v2", "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")

        assert res.error is False
        assert res.data.chain_id == 1
        assert res.data.chain_name == "eth-mainnet"
        assert len(res.data.items) > 0
    
    def test_get_lp_token_view_error(self, client: CovalentClient):
        res = client.xyk_service.get_lp_token_view("eth-mainnet", "uniswap_v3", "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")

        assert res.error is True
    
    def test_get_transactions_for_dex_success(self, client: CovalentClient):
        res = client.xyk_service.get_transactions_for_dex(Chains.ETH_MAINNET, "uniswap_v2")

        assert res.error is False
        assert res.data.chain_id == 1
        assert res.data.chain_name == "eth-mainnet"
        assert len(res.data.items) > 0
    
    def test_get_transactions_for_dex_error(self, client: CovalentClient):
        res = client.xyk_service.get_transactions_for_dex("eth-mainnet", "uniswap_v3")

        assert res.error is True