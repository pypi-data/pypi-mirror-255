from typing import Literal, Optional

from covalent.services.util.api_key_validator import ApiKeyValidator
from .services.security_service import SecurityService
from .services.balance_service import BalanceService
from .services.base_service import BaseService
from .services.nft_service import NftService
from .services.pricing_service import PricingService
from .services.transaction_service import TransactionService
from .services.xyk_service import XykService
from deprecated import deprecated


class CovalentClient:
    """ CovalentClient Class """

    security_service: SecurityService
  
    balance_service: BalanceService
  
    base_service: BaseService
  
    nft_service: NftService
  
    pricing_service: PricingService
  
    transaction_service: TransactionService
  
    xyk_service: XykService

    __is_key_valid: bool
    
  
    def __init__(self, api_key: str, debug: Optional[bool] = False):
        
        validator = ApiKeyValidator(api_key)
        self.__is_key_valid = validator.is_valid_api_key()

        self.security_service = SecurityService(api_key, self.__is_key_valid, debug)
        self.balance_service = BalanceService(api_key, self.__is_key_valid, debug)
        self.base_service = BaseService(api_key, self.__is_key_valid, debug)
        self.nft_service = NftService(api_key, self.__is_key_valid, debug)
        self.pricing_service = PricingService(api_key, self.__is_key_valid, debug)
        self.transaction_service = TransactionService(api_key, self.__is_key_valid, debug)
        self.xyk_service = XykService(api_key, self.__is_key_valid, debug)
        

@deprecated("'Client' is deprecated, use 'CovalentClient' instead")
class Client:
    """
    Client is deprecated and will be removed after Oct 31, 2023.
    
    Please use CovalentClient instead.
    """
    
    security_service: SecurityService
  
    balance_service: BalanceService
  
    base_service: BaseService
  
    nft_service: NftService
  
    pricing_service: PricingService
  
    transaction_service: TransactionService
  
    xyk_service: XykService
    
    __is_key_valid: bool
  
    def __init__(self, api_key: str, debug: Optional[bool] = False):
        
        validator = ApiKeyValidator(api_key)
        self.__is_key_valid = validator.is_valid_api_key()

        self.security_service = SecurityService(api_key, self.__is_key_valid, debug)
        self.balance_service = BalanceService(api_key, self.__is_key_valid, debug)
        self.base_service = BaseService(api_key, self.__is_key_valid, debug)
        self.nft_service = NftService(api_key, self.__is_key_valid, debug)
        self.pricing_service = PricingService(api_key, self.__is_key_valid, debug)
        self.transaction_service = TransactionService(api_key, self.__is_key_valid, debug)
        self.xyk_service = XykService(api_key, self.__is_key_valid, debug)