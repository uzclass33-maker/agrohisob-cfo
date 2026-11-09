import pytest
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def apply_default_test_auth(request):
    """
    Provides deterministic test authentication context for legacy test modules,
    ensuring regression test suites run cleanly while server-side authentication
    and tenant authorization remain strictly active on all endpoints.
    
    Security-specific test modules (e.g. test_auth_*) manage their own headers
    to test 401 Unauthorized and 403 Forbidden conditions explicitly.
    """
    if "test_auth" in request.module.__name__:
        return

    mod = request.module
    if hasattr(mod, "client") and isinstance(getattr(mod, "client"), TestClient):
        client = getattr(mod, "client")
        if "Authorization" not in client.headers:
            client.headers["Authorization"] = "Bearer test-token-admin"
