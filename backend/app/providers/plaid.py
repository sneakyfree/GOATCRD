"""
GOATCRD Plaid Integration Provider
Bank account linking and cash flow verification
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel


class PlaidProductType(str, Enum):
    """Plaid product types."""
    TRANSACTIONS = "transactions"
    AUTH = "auth"
    IDENTITY = "identity"
    ASSETS = "assets"
    LIABILITIES = "liabilities"


class PlaidAccountType(str, Enum):
    """Plaid account types."""
    DEPOSITORY = "depository"
    CREDIT = "credit"
    LOAN = "loan"
    INVESTMENT = "investment"


@dataclass
class PlaidLinkToken:
    """Plaid Link token for frontend."""
    link_token: str
    expiration: datetime
    request_id: str


@dataclass
class PlaidAccessToken:
    """Plaid access token for API calls."""
    access_token: str
    item_id: str
    request_id: str


@dataclass
class PlaidAccount:
    """Plaid account information."""
    account_id: str
    name: str
    official_name: str | None
    type: PlaidAccountType
    subtype: str | None
    mask: str | None
    available_balance: float | None
    current_balance: float | None


@dataclass
class PlaidTransaction:
    """Plaid transaction."""
    transaction_id: str
    account_id: str
    amount: float
    date: str
    name: str
    category: list[str]
    pending: bool


class PlaidProvider:
    """
    Plaid integration for bank account linking.
    
    Provides:
    - Link token generation for frontend
    - Access token exchange
    - Account balance retrieval
    - Transaction history
    - Identity verification
    """
    
    def __init__(
        self,
        client_id: str,
        secret: str,
        environment: str = "sandbox",
    ):
        self.client_id = client_id
        self.secret = secret
        self.environment = environment
        self.base_url = self._get_base_url(environment)
    
    def _get_base_url(self, env: str) -> str:
        """Get Plaid API base URL for environment."""
        urls = {
            "sandbox": "https://sandbox.plaid.com",
            "development": "https://development.plaid.com",
            "production": "https://production.plaid.com",
        }
        return urls.get(env, urls["sandbox"])
    
    async def create_link_token(
        self,
        user_id: UUID,
        products: list[PlaidProductType] | None = None,
        redirect_uri: str | None = None,
    ) -> PlaidLinkToken:
        """
        Create a Link token for initializing Plaid Link.
        
        Args:
            user_id: Consumer ID for Link session
            products: Plaid products to request
            redirect_uri: OAuth redirect URI
        
        Returns:
            PlaidLinkToken for frontend initialization
        """
        # In production, would make actual API call
        # import httpx
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"{self.base_url}/link/token/create",
        #         json={
        #             "client_id": self.client_id,
        #             "secret": self.secret,
        #             "user": {"client_user_id": str(user_id)},
        #             "client_name": "GOATCRD",
        #             "products": products or ["transactions", "auth"],
        #             "country_codes": ["US"],
        #             "language": "en",
        #             "redirect_uri": redirect_uri,
        #         },
        #     )
        #     data = response.json()
        
        # Mock response for development
        return PlaidLinkToken(
            link_token=f"link-sandbox-{uuid4().hex[:16]}",
            expiration=datetime.now(timezone.utc),
            request_id=str(uuid4()),
        )
    
    async def exchange_public_token(
        self,
        public_token: str,
    ) -> PlaidAccessToken:
        """
        Exchange public token for access token.
        
        Called after user completes Plaid Link flow.
        """
        # Mock response for development
        return PlaidAccessToken(
            access_token=f"access-sandbox-{uuid4().hex[:32]}",
            item_id=f"item-{uuid4().hex[:16]}",
            request_id=str(uuid4()),
        )
    
    async def get_accounts(
        self,
        access_token: str,
    ) -> list[PlaidAccount]:
        """Get linked accounts."""
        # Mock response for development
        return [
            PlaidAccount(
                account_id=f"account-{uuid4().hex[:8]}",
                name="Checking",
                official_name="Premium Checking Account",
                type=PlaidAccountType.DEPOSITORY,
                subtype="checking",
                mask="1234",
                available_balance=5432.10,
                current_balance=5532.10,
            ),
            PlaidAccount(
                account_id=f"account-{uuid4().hex[:8]}",
                name="Savings",
                official_name="High Yield Savings",
                type=PlaidAccountType.DEPOSITORY,
                subtype="savings",
                mask="5678",
                available_balance=12500.00,
                current_balance=12500.00,
            ),
        ]
    
    async def get_transactions(
        self,
        access_token: str,
        start_date: str,
        end_date: str,
    ) -> list[PlaidTransaction]:
        """Get transaction history."""
        # Mock response for development
        return [
            PlaidTransaction(
                transaction_id=f"tx-{uuid4().hex[:8]}",
                account_id="account-checking",
                amount=-125.50,
                date="2026-01-20",
                name="Electric Company",
                category=["Utilities", "Electric"],
                pending=False,
            ),
        ]
    
    async def get_identity(
        self,
        access_token: str,
    ) -> dict[str, Any]:
        """Get identity information for verification."""
        # Mock response for development
        return {
            "accounts": [
                {
                    "account_id": "account-checking",
                    "owners": [
                        {
                            "names": ["John Doe"],
                            "addresses": [
                                {
                                    "data": {
                                        "city": "San Francisco",
                                        "region": "CA",
                                        "postal_code": "94107",
                                        "country": "US",
                                    },
                                    "primary": True,
                                }
                            ],
                            "emails": [{"data": "john.doe@email.com", "primary": True}],
                            "phone_numbers": [{"data": "+14155551234", "primary": True}],
                        }
                    ],
                }
            ],
        }
    
    async def invalidate_access_token(
        self,
        access_token: str,
    ) -> bool:
        """
        Invalidate access token (for consent revocation).
        
        Called when user revokes consent.
        """
        # In production, would make actual API call
        return True


# Factory function
def create_plaid_provider(
    client_id: str | None = None,
    secret: str | None = None,
    environment: str = "sandbox",
) -> PlaidProvider:
    """Create Plaid provider instance."""
    return PlaidProvider(
        client_id=client_id or "plaid_client_id",
        secret=secret or "plaid_secret",
        environment=environment,
    )
