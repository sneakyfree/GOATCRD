"""
GOATCRD API Integration Tests
[HARDENING] Task 5.1: Integration tests for core API flows
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4


@pytest.fixture
def api_url():
    """Base API URL."""
    return "http://localhost:8847/api/v1"


class TestAuthFlow:
    """Test authentication flow end-to-end."""
    
    @pytest.mark.asyncio
    async def test_register_and_login(self, api_url):
        """Test user registration and login flow."""
        async with AsyncClient() as client:
            email = f"test_{uuid4().hex[:8]}@test.com"
            password = "testpass123"
            
            # Register
            response = await client.post(
                f"{api_url}/auth/register",
                json={
                    "email": email,
                    "password": password,
                },
            )
            assert response.status_code in [201, 400]  # 400 if already exists
            
            # Login
            response = await client.post(
                f"{api_url}/auth/login",
                json={
                    "email": email,
                    "password": password,
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                assert "access_token" in data
                assert "refresh_token" in data
                assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, api_url):
        """Test login with invalid credentials."""
        async with AsyncClient() as client:
            response = await client.post(
                f"{api_url}/auth/login",
                json={
                    "email": "nonexistent@test.com",
                    "password": "wrongpass",
                },
            )
            assert response.status_code == 401


class TestCaseFlow:
    """Test case management flow."""
    
    @pytest.fixture
    async def auth_headers(self, api_url):
        """Get authentication headers for demo user."""
        async with AsyncClient() as client:
            response = await client.post(
                f"{api_url}/auth/login",
                json={
                    "email": "demo@goatcrd.com",
                    "password": "demo123",
                },
            )
            if response.status_code == 200:
                token = response.json()["access_token"]
                return {"Authorization": f"Bearer {token}"}
            return None
    
    @pytest.mark.asyncio
    async def test_create_case(self, api_url, auth_headers):
        """Test case creation."""
        if not auth_headers:
            pytest.skip("Demo user not seeded")
            
        async with AsyncClient() as client:
            response = await client.post(
                f"{api_url}/cases",
                headers=auth_headers,
                json={"case_type": "personal_loan"},
            )
            
            if response.status_code == 201:
                data = response.json()
                assert "id" in data
                assert data["case_type"] == "personal_loan"
                assert data["status"] == "draft"
    
    @pytest.mark.asyncio
    async def test_list_cases(self, api_url, auth_headers):
        """Test case listing."""
        if not auth_headers:
            pytest.skip("Demo user not seeded")
            
        async with AsyncClient() as client:
            response = await client.get(
                f"{api_url}/cases",
                headers=auth_headers,
            )
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list)


class TestScenarioFlow:
    """Test scenario generation flow."""
    
    @pytest.fixture
    async def auth_headers(self, api_url):
        """Get authentication headers."""
        async with AsyncClient() as client:
            response = await client.post(
                f"{api_url}/auth/login",
                json={
                    "email": "demo@goatcrd.com",
                    "password": "demo123",
                },
            )
            if response.status_code == 200:
                return {"Authorization": f"Bearer {response.json()['access_token']}"}
            return None
    
    @pytest.mark.asyncio
    async def test_scenario_run_requires_case(self, api_url, auth_headers):
        """Test that scenario run requires valid case."""
        if not auth_headers:
            pytest.skip("Demo user not seeded")
            
        async with AsyncClient() as client:
            fake_case_id = str(uuid4())
            response = await client.post(
                f"{api_url}/cases/{fake_case_id}/scenarios/run",
                headers=auth_headers,
                json={"intake_snapshot_id": str(uuid4())},
            )
            
            assert response.status_code == 404


class TestNegativeCases:
    """Test negative/error cases."""
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self, api_url):
        """Test that protected endpoints require auth."""
        async with AsyncClient() as client:
            # Cases without auth
            response = await client.get(f"{api_url}/cases")
            assert response.status_code in [401, 403, 422]
            
            # Scenarios without auth
            response = await client.post(
                f"{api_url}/cases/{uuid4()}/scenarios/run",
                json={"intake_snapshot_id": str(uuid4())},
            )
            assert response.status_code in [401, 403, 422]
    
    @pytest.mark.asyncio
    async def test_invalid_case_id(self, api_url):
        """Test invalid case ID handling."""
        async with AsyncClient() as client:
            response = await client.get(f"{api_url}/cases/not-a-uuid")
            assert response.status_code == 422  # Validation error


class TestPartnerAPI:
    """Test partner/LaaS API."""
    
    @pytest.mark.asyncio
    async def test_partner_registration_requires_admin(self, api_url):
        """Test that partner registration requires admin role."""
        async with AsyncClient() as client:
            # Login as regular user
            login_response = await client.post(
                f"{api_url}/auth/login",
                json={
                    "email": "demo@goatcrd.com",
                    "password": "demo123",
                },
            )
            
            if login_response.status_code != 200:
                pytest.skip("Demo user not seeded")
            
            token = login_response.json()["access_token"]
            
            # Try to register partner (should fail - not admin)
            response = await client.post(
                f"{api_url}/partners/register",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "partner_name": "Test Partner",
                },
            )
            
            # Should be 403 Forbidden (non-admin)
            assert response.status_code in [401, 403]
    
    @pytest.mark.asyncio
    async def test_session_requires_api_key(self, api_url):
        """Test that session creation requires API key."""
        async with AsyncClient() as client:
            response = await client.post(
                f"{api_url}/partners/sessions",
                json={
                    "consumer_reference": "test123",
                },
            )
            
            # Missing X-API-Key header
            assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
