from covalent import CovalentClient
import pytest
import os

from covalent.services.util.chains import Chains



class TestTransactionService:
    
    @pytest.fixture
    def client(self):
        return CovalentClient(os.environ.get('COVALENT_API_KEY'))

    def test_success_for_get_transaction(self, client: CovalentClient):
        res =  client.transaction_service.get_transaction(Chains.ETH_MAINNET, "0xb27a3a3d660b7d679ebbd7065635c8c3613e32eb0ebae24863a6375d73d1a128")
        assert res.error is False
        assert res.data.chain_id == 1
        assert res.data.chain_name == "eth-mainnet"
        assert len(res.data.items) > 0
        assert res.data.items[0].tx_hash == "0xb27a3a3d660b7d679ebbd7065635c8c3613e32eb0ebae24863a6375d73d1a128"
        
            
    def test_incorrect_hash_for_transaction(self, client: CovalentClient):
        res =  client.transaction_service.get_transaction(Chains.ETH_MAINNET, "0xtest")
        assert res.error is True
        assert res.data is None
        assert res.error_code == 400
        assert res.error_message == "0xtest is an invalid transaction hash."
    
    def test_success_for_get_transaction_summary(self, client: CovalentClient):
        res =  client.transaction_service.get_transaction_summary("eth-mainnet", "demo.eth")
        assert res.error is False
        assert res.data.chain_id == 1
        assert res.data.chain_name == "eth-mainnet"
        assert res.data.address == "0xfc43f5f9dd45258b3aff31bdbe6561d97e8b71de"
        assert len(res.data.items) > 0
    
    def test_incorrect_address_for_get_transaction_summary(self, client: CovalentClient):
        res =  client.transaction_service.get_transaction_summary("eth-mainnet", "0x123")
        assert res.error is True
        assert res.data is None
        assert res.error_code == 400
        assert res.error_message == "Malformed address provided: 0x123"
    
    def test_success_for_transaction_block(self, client: CovalentClient):
        res =  client.transaction_service.get_transactions_for_block(Chains.ETH_MAINNET, 17685920)
        assert res.error is False
        assert res.data.chain_name == "eth-mainnet"
        assert res.data.chain_id == 1
        assert res.data.items[0].block_height == 17685920

    def test_invalid_block_height(self, client: CovalentClient):
        res =  client.transaction_service.get_transactions_for_block(Chains.ETH_MAINNET, 100000000)
        assert res.error is True
        assert res.data is None
        assert res.error_code == 404
        assert res.error_message == "Block not found: chain-height '100000000' has not yet been reached for chain 'eth-mainnet'."
    
    def test_no_logs_for_transaction_block(self, client: CovalentClient):
        res =  client.transaction_service.get_transactions_for_block("eth-mainnet", 17685920, "CAD", True)
        assert res.error is False
        assert res.data.items[0].log_events is None   
    
    def test_success_for_get_transactions_v3(self, client: CovalentClient):
        res =  client.transaction_service.get_transactions_for_address_v3(Chains.ETH_MAINNET, "demo.eth", 0)
        assert res.error is False
        assert res.data.chain_name == "eth-mainnet"
        assert res.data.chain_id == 1
        assert len(res.data.items) > 0
        
    def test_success_for_get_time_bucket_transactions_for_address(self, client: CovalentClient):
        res = client.transaction_service.get_time_bucket_transactions_for_address(Chains.ETH_MAINNET, "demo.eth", 1799272)
        assert res.error is False
        assert res.data.chain_name == "eth-mainnet"
        assert res.data.chain_id == 1
        assert len(res.data.items) > 0
    
    def test_failed_for_get_time_bucket_transactions_for_address(self, client: CovalentClient):
        res =  client.transaction_service.get_time_bucket_transactions_for_address(Chains.ETH_MAINNET, "demo", 1799272)
        assert res.error is True
    
    def test_prev_for_get_time_bucket_transactions_for_address(self, client: CovalentClient):
        res = client.transaction_service.get_time_bucket_transactions_for_address(Chains.ETH_MAINNET, "demo.eth", 1799272)
        prevPage = res.data.prev()
        assert prevPage.error is False
    
    def test_next_for_get_time_bucket_transactions_for_address(self, client: CovalentClient):
        res =  client.transaction_service.get_time_bucket_transactions_for_address(Chains.ETH_MAINNET, "demo.eth", 1990549)
        nextPage = res.data.next()
        assert nextPage.error is True
        assert nextPage.error_code == 400
        assert nextPage.error_message == "Invalid URL: URL link cannot be null"
    
    def test_success_for_get_transactions_for_block_hash_by_page(self, client: CovalentClient):
        res = client.transaction_service.get_transactions_for_block_hash_by_page(Chains.ETH_MAINNET, "0x4ee50495ce7fbc4bfe412c38052eb8ca1bc470c0c07d756757f2fced9ad9d60b", 0)
        assert res.error is False
        assert res.data.chain_name == "eth-mainnet"
        assert res.data.chain_id == 1
        assert len(res.data.items) > 0
    
    def test_next_success_for_get_transactions_for_block_hash_by_page(self, client: CovalentClient):
        res =  client.transaction_service.get_transactions_for_block_hash_by_page(Chains.ETH_MAINNET, "0x4ee50495ce7fbc4bfe412c38052eb8ca1bc470c0c07d756757f2fced9ad9d60b", 0)
        nextPage = res.data.next()
        assert nextPage.error is False
    
    def test_success_for_get_transactions_for_block_hash(self, client: CovalentClient):
        res = client.transaction_service.get_transactions_for_block_hash(Chains.ETH_MAINNET, "0x4ee50495ce7fbc4bfe412c38052eb8ca1bc470c0c07d756757f2fced9ad9d60b")
        assert res.error is False
        assert res.data.chain_name == "eth-mainnet"
        assert res.data.chain_id == 1
        assert len(res.data.items) > 0
    
    def test_empty_for_get_transactions_for_block_hash(self, client: CovalentClient):
        res =  client.transaction_service.get_transactions_for_block_hash(Chains.ETH_MAINNET, "0x0")
        assert res.error is False
        assert res.data.chain_name == "eth-mainnet"
        assert res.data.chain_id == 1
        assert len(res.data.items) == 0
    
    @pytest.mark.asyncio
    async def test_success_for_get_all_transactions(self, client: CovalentClient):
        async for res in client.transaction_service.get_all_transactions_for_address("eth-mainnet", "demo.eth"):
            assert res is not None
    
    
    @pytest.mark.asyncio
    async def test_malformed_address(self, client: CovalentClient):
        with pytest.raises(Exception) as exc_info:
            async for res in client.transaction_service.get_all_transactions_for_address(Chains.ETH_MAINNET, "0x1233"):
                assert "An error occured 400 : Malformed address provided: 0x123123" in str(exc_info.value)

    
    @pytest.mark.asyncio
    async def test_quote_currency(self, client: CovalentClient):
        async for res in client.transaction_service.get_all_transactions_for_address("eth-mainnet", "demo.eth", "CAD"):
            assert res is not None
    
    
    @pytest.mark.asyncio
    async def test_no_logs_for_get_all_transactions(self, client: CovalentClient):
        async for res in client.transaction_service.get_all_transactions_for_address(Chains.ETH_MAINNET, "demo.eth", "CAD", True):
            assert res.log_events is None
    
    
    
    
        
    
    

