import pytest
import os
from datetime import datetime
from covalent import CovalentClient
from covalent.services.util.chains import Chains


class TestBaseService:
    """ base service testing class """

    @pytest.fixture
    def client(self):
        """ initialize client """
        return CovalentClient(os.environ.get('COVALENT_API_KEY'))

    # get block endpoint testing
    def test_get_block_success(self, client: CovalentClient):
        """ test for get block endpoint success """
        block = client.base_service.get_block("eth-mainnet", "17679441")
        assert block.error is False
        assert block.data.chain_id == 1
        assert block.data.chain_name == "eth-mainnet"
        assert block.data.items[0].height == 17679441
        assert block.data.items[0].signed_at == datetime.fromisoformat("2023-07-12T19:06:11Z")

    def test_get_block_fail(self, client: CovalentClient):
        """ test for get block endpoint fail """
        block_fail = client.base_service.get_block("eth-mainnet", "-1")
        assert block_fail.error is True

    # get resolved address endpoint testing
    def test_get_resolved_address_success(self, client: CovalentClient):
        """ test for get resolved address endpoint success """
        res_ens = client.base_service.get_resolved_address("eth-mainnet", "demo.eth")
        assert res_ens.error is False
        assert res_ens.data.items[0].address == "0xfc43f5f9dd45258b3aff31bdbe6561d97e8b71de"

        res_rns = client.base_service.get_resolved_address("rsk-mainnet", "dylan.rsk")
        assert res_rns.error is False
        assert res_rns.data.items[0].address == "0x92659ca386f8805f7c480711cee92e0e0eb5406e"

        res_lens = client.base_service.get_resolved_address("eth-mainnet", "@lensprotocol")
        assert res_lens.error is False
        assert res_lens.data.items[0].address == "0x05092cf69bdd435f7ba4b8ef97c9caecf2ba69ad"

        res_unstop_dom = client.base_service.get_resolved_address("eth-mainnet", "jim-unstoppable.x")
        assert res_unstop_dom.error is False
        assert res_unstop_dom.data.items[0].address == "0x57a82545be709963f0182b69f6e9b6f00b977592"

    def test_get_resolved_address_fail(self, client: CovalentClient):
        """ test for get resolved address endpoint fail """
        res_fail = client.base_service.get_resolved_address("eth-mainnet", "alice.rsk")
        assert res_fail.error is True

    # get block height endpoint testing
    @pytest.mark.asyncio
    async def test_get_block_height_success(self, client: CovalentClient):
        """ test for get block height endpoint success """
        async for res in client.base_service.get_block_heights("eth-mainnet", "2023-01-01", "2023-01-02"):
            assert res is not None

    @pytest.mark.asyncio
    async def test_get_block_height_fail(self, client: CovalentClient):
        """ test for get block height endpoint fail """
        with pytest.raises(Exception) as exc_info:
            async for res in client.base_service.get_block_heights("eth-mainnet", "2023-01-03", "2023-01-02"):
                assert "An error occured 400 : Invalid path parameter(s), start_date is after end_date.  start_date: 2023-01-03 end_date: 2023-01-02" in str(exc_info.value)
        
    # get logs endpoint testing
    def test_get_logs_success(self, client: CovalentClient):
        """ test for get logs endpoint success """
        logs_ = client.base_service.get_logs("eth-mainnet")
        assert logs_.error is False
        assert logs_.data.chain_id == 1
        assert logs_.data.chain_name == "eth-mainnet"
        assert len(logs_.data.items) > 0

    def test_get_logs_fail(self, client: CovalentClient):
        """ test for get logs endpoint fail """
        logs_fail = client.base_service.get_logs("eth-mainnet", "-1")
        assert logs_fail.error is True

    # get log events by address endpoint testing
    @pytest.mark.asyncio
    async def test_get_log_events_success(self, client: CovalentClient):
        """ test for get log events by address endpoint success """
        async for res in client.base_service.get_log_events_by_address("eth-mainnet", "0xdac17f958d2ee523a2206206994597c13d831ec7", 17679143, "17679148"):
            assert res is not None

    @pytest.mark.asyncio
    async def test_get_log_events_fail(self, client: CovalentClient):
        """ test for get log events by address endpoint fail """
        with pytest.raises(Exception) as exc_info:
            async for res in client.base_service.get_log_events_by_address("eth-mainnet", "0xdac17f958d2ee523a2206206994597c13d831e"):
                assert "An error occured 400 : Malformed address provided: 0xdac17f958d2ee523a2206206994597c13d831e" in str(exc_info.value)
        
    # get log events by topic hash endpoint testing
    @pytest.mark.asyncio
    async def test_get_log_events_hash_success(self, client: CovalentClient):
        """ test for get log events by hash endpoint success """
        async for res in client.base_service.get_log_events_by_topic_hash("eth-mainnet", "0x27f12abfe35860a9a927b465bb3d4a9c23c8428174b83f278fe45ed7b4da2662", 17666774, "17679143"):
            assert res is not None

    @pytest.mark.asyncio
    async def test_get_log_events_hash_fail(self, client: CovalentClient):
        """ test for get log events by hash endpoint fail """
        with pytest.raises(Exception) as exc_info:
            async for res in client.base_service.get_log_events_by_topic_hash("eth-mainnet", "0xdac17f958d2ee523a2206206994597c13d831e", 17666774, "17679143"):
                assert "An error occured 400 : topic hash '0xdac17f958d2ee523a2206206994597c13d831e' malformed." in str(exc_info.value)
        
    # get all chains endpoint testing
    def test_get_chains_success(self, client: CovalentClient):
        """ test for get chains endpoint success """
        all_chains = client.base_service.get_all_chains()
        assert all_chains.error is False
        assert len(all_chains.data.items) > 0

    # get all chains status endpoint testing
    def test_get_chains_status_success(self, client: CovalentClient):
        """ test for get chains status endpoint fail """
        chain_status = client.base_service.get_all_chain_status()
        assert chain_status.error is False
        assert len(chain_status.data.items) > 0
        
    # get address activity endpoint testing
    def test_get_address_activity_success(self, client: CovalentClient):
        """ test for get address activity endpoint success """
        chain_status = client.base_service.get_address_activity("0x39ee2c7b3cb80254225884ca001f57118c8f21b6")
        assert chain_status.error is False
        assert len(chain_status.data.items) > 0

    # get token holders by page endpoint testing sucess
    def test_get_block_heights_by_page_success(self, client: CovalentClient):
        """ test for get address activity endpoint success """
        blockHeightsByPage = client.base_service.get_block_heights_by_page(Chains.ETH_MAINNET, "2023-01-01", "2023-01-02")
        assert blockHeightsByPage.error is False
        assert blockHeightsByPage.data.chain_id == 1
        assert blockHeightsByPage.data.chain_name == "eth-mainnet"
        assert len(blockHeightsByPage.data.items) > 0
    
    # get token holders by page endpoint testing fail
    def test_get_block_heights_by_page_fail(self, client: CovalentClient):
        """ test for get address activity endpoint fail """
        blockHeightsByPage = client.base_service.get_block_heights_by_page("eth-mainnet", "2024-01-01", "20234-01-02")
        assert blockHeightsByPage.error is True

    def test_get_log_events_contract_by_page_sucess(self, client: CovalentClient):
        """ test for get log events contract by page endpoint success """
        logEventsContractByPage = client.base_service.get_log_events_by_address_by_page(Chains.ETH_MAINNET, "0xdac17f958d2ee523a2206206994597c13d831ec7", 17679143, "17679148")
        assert logEventsContractByPage.error is False
        assert logEventsContractByPage.data.chain_id == 1
        assert logEventsContractByPage.data.chain_name == "eth-mainnet"
        assert len(logEventsContractByPage.data.items) > 0
    
    def test_get_log_events_contract_by_page_fail(self, client: CovalentClient):
        """ test for get log events contract by page endpoint fail """
        logEventsContractByPage = client.base_service.get_log_events_by_address_by_page("eth-mainnet", "0xdac17f958d2ee523a2206206994597c13d831e", 17679143, "17679148")
        assert logEventsContractByPage.error is True
    
    def test_get_log_events_hash_by_page_sucess(self, client: CovalentClient):
        """ test for get log events hash by page endpoint success """
        logEventsHashByPage = client.base_service.get_log_events_by_topic_hash_by_page(Chains.ETH_MAINNET, "0x27f12abfe35860a9a927b465bb3d4a9c23c8428174b83f278fe45ed7b4da2662", 17666774, "17679143")
        assert logEventsHashByPage.error is False
        assert logEventsHashByPage.data.chain_id == 1
        assert logEventsHashByPage.data.chain_name == "eth-mainnet"
        assert len(logEventsHashByPage.data.items) > 0
    
    def test_get_log_events_hash_by_page_fail(self, client: CovalentClient):
        """ test for get log events hash by page endpoint fail """
        logEventsHashByPage = client.base_service.get_log_events_by_topic_hash_by_page(Chains.ETH_MAINNET, "0xdac17f958d2ee523a2206206994597c13d831e", 17679143, "17679148")
        assert logEventsHashByPage.error is True
    
    def test_get_gas_prices_success(self, client: CovalentClient):
        prices = client.base_service.get_gas_prices(Chains.ETH_MAINNET, "uniswapv3")
        assert prices.error is False

    def test_get_gas_prices_event_types(self, client: CovalentClient):
        prices = client.base_service.get_gas_prices(Chains.ETH_MAINNET, "uniswapv3")
        assert prices.error is False
        assert prices.data.event_type == "uniswapv3"

    def test_get_gas_prices_quote_currency(self, client: CovalentClient):
        prices = client.base_service.get_gas_prices(Chains.ETH_MAINNET, "uniswapv3", quote_currency="CAD")
        assert prices.error is False
        assert prices.data.quote_currency == "CAD"