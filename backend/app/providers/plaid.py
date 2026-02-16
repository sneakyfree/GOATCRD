"""
GOATCRD Plaid Provider
Alternative data integration with sandbox/mock fallback.
"""
import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class PlaidProvider:
    """
    Plaid integration provider with mock fallback.
    
    When PLAID_CLIENT_ID is empty (default), returns mock data
    suitable for demos and development. When configured, calls
    the real Plaid API in the configured environment (sandbox/dev/prod).
    """
    
    def __init__(self):
        self.client_id = settings.plaid_client_id
        self.secret = settings.plaid_secret
        self.env = settings.plaid_env
        self.is_live = bool(self.client_id and self.secret)
    
    async def create_link_token(self, user_id: str) -> dict[str, Any]:
        """Create a Plaid Link token for the frontend."""
        if not self.is_live:
            return self._mock_link_token(user_id)
        
        try:
            import plaid
            from plaid.api import plaid_api
            from plaid.model.link_token_create_request import LinkTokenCreateRequest
            from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
            from plaid.model.products import Products
            from plaid.model.country_code import CountryCode
            
            configuration = plaid.Configuration(
                host=self._get_host(),
                api_key={"clientId": self.client_id, "secret": self.secret},
            )
            api_client = plaid.ApiClient(configuration)
            client = plaid_api.PlaidApi(api_client)
            
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(client_user_id=user_id),
                client_name="GOATCRD",
                products=[Products("transactions"), Products("auth")],
                country_codes=[CountryCode("US")],
                language="en",
            )
            response = client.link_token_create(request)
            logger.info("Plaid link token created for user=%s", user_id)
            return {"link_token": response.link_token, "expiration": str(response.expiration)}
            
        except ImportError:
            logger.warning("plaid-python not installed — using mock")
            return self._mock_link_token(user_id)
        except Exception as e:
            logger.error("Plaid link_token_create error: %s", str(e))
            return self._mock_link_token(user_id)
    
    async def exchange_public_token(self, public_token: str) -> dict[str, Any]:
        """Exchange a public token for an access token."""
        if not self.is_live:
            return self._mock_exchange(public_token)
        
        try:
            import plaid
            from plaid.api import plaid_api
            from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
            
            configuration = plaid.Configuration(
                host=self._get_host(),
                api_key={"clientId": self.client_id, "secret": self.secret},
            )
            api_client = plaid.ApiClient(configuration)
            client = plaid_api.PlaidApi(api_client)
            
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = client.item_public_token_exchange(request)
            logger.info("Plaid token exchanged, item_id=%s", response.item_id)
            return {"access_token": response.access_token, "item_id": response.item_id}
            
        except ImportError:
            return self._mock_exchange(public_token)
        except Exception as e:
            logger.error("Plaid exchange error: %s", str(e))
            return self._mock_exchange(public_token)
    
    async def get_accounts(self, access_token: str) -> list[dict[str, Any]]:
        """Get linked accounts."""
        if not self.is_live:
            return self._mock_accounts()
        
        try:
            import plaid
            from plaid.api import plaid_api
            from plaid.model.accounts_get_request import AccountsGetRequest
            
            configuration = plaid.Configuration(
                host=self._get_host(),
                api_key={"clientId": self.client_id, "secret": self.secret},
            )
            api_client = plaid.ApiClient(configuration)
            client = plaid_api.PlaidApi(api_client)
            
            request = AccountsGetRequest(access_token=access_token)
            response = client.accounts_get(request)
            
            return [
                {
                    "account_id": str(acct.account_id),
                    "name": acct.name,
                    "type": str(acct.type),
                    "subtype": str(acct.subtype),
                    "balance_current": float(acct.balances.current or 0),
                    "balance_available": float(acct.balances.available or 0),
                }
                for acct in response.accounts
            ]
        except ImportError:
            return self._mock_accounts()
        except Exception as e:
            logger.error("Plaid accounts error: %s", str(e))
            return self._mock_accounts()
    
    async def get_transactions(
        self, access_token: str, start_date: str, end_date: str
    ) -> list[dict[str, Any]]:
        """Get transactions for the date range."""
        if not self.is_live:
            return self._mock_transactions()
        
        try:
            import plaid
            from plaid.api import plaid_api
            from plaid.model.transactions_get_request import TransactionsGetRequest
            
            configuration = plaid.Configuration(
                host=self._get_host(),
                api_key={"clientId": self.client_id, "secret": self.secret},
            )
            api_client = plaid.ApiClient(configuration)
            client = plaid_api.PlaidApi(api_client)
            
            from datetime import date
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=date.fromisoformat(start_date),
                end_date=date.fromisoformat(end_date),
            )
            response = client.transactions_get(request)
            
            return [
                {
                    "transaction_id": str(txn.transaction_id),
                    "amount": float(txn.amount),
                    "date": str(txn.date),
                    "name": txn.name,
                    "category": txn.category,
                    "merchant_name": txn.merchant_name,
                }
                for txn in response.transactions
            ]
        except ImportError:
            return self._mock_transactions()
        except Exception as e:
            logger.error("Plaid transactions error: %s", str(e))
            return self._mock_transactions()
    
    def _get_host(self) -> str:
        hosts = {
            "sandbox": "https://sandbox.plaid.com",
            "development": "https://development.plaid.com",
            "production": "https://production.plaid.com",
        }
        return hosts.get(self.env, hosts["sandbox"])
    
    # --- Mock data for dev/demo mode ---
    
    def _mock_link_token(self, user_id: str) -> dict[str, Any]:
        return {
            "link_token": f"link-sandbox-mock-{user_id[:8]}",
            "expiration": "2026-12-31T23:59:59Z",
            "_mock": True,
        }
    
    def _mock_exchange(self, public_token: str) -> dict[str, Any]:
        return {
            "access_token": f"access-sandbox-mock-{public_token[:8]}",
            "item_id": "mock-item-001",
            "_mock": True,
        }
    
    def _mock_accounts(self) -> list[dict[str, Any]]:
        return [
            {
                "account_id": "mock-checking-001",
                "name": "Primary Checking",
                "type": "depository",
                "subtype": "checking",
                "balance_current": 4250.00,
                "balance_available": 4100.00,
                "_mock": True,
            },
            {
                "account_id": "mock-savings-001",
                "name": "Savings Account",
                "type": "depository",
                "subtype": "savings",
                "balance_current": 12500.00,
                "balance_available": 12500.00,
                "_mock": True,
            },
        ]
    
    def _mock_transactions(self) -> list[dict[str, Any]]:
        return [
            {
                "transaction_id": "mock-txn-001",
                "amount": -2100.00,
                "date": "2026-01-01",
                "name": "Monthly Rent Payment",
                "category": ["Rent"],
                "merchant_name": "Property Management Co",
                "_mock": True,
            },
            {
                "transaction_id": "mock-txn-002",
                "amount": -185.50,
                "date": "2026-01-15",
                "name": "Electric Utility",
                "category": ["Utilities"],
                "merchant_name": "City Power & Light",
                "_mock": True,
            },
            {
                "transaction_id": "mock-txn-003",
                "amount": 3500.00,
                "date": "2026-01-15",
                "name": "Direct Deposit - Payroll",
                "category": ["Income"],
                "merchant_name": None,
                "_mock": True,
            },
        ]
