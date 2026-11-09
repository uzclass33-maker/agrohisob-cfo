"""
AgroHisob CFO - Cryptographic Security & JWT Verification
Provides deterministic, zero-dependency JWT parsing, validation and signature verification.
"""

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, Optional
from app.config import settings
from app.auth.models import AuthenticatedUser, OrgMembership, UserRole

# In-memory mock/demo tenant memberships for development, demo, and test environments
DEMO_MEMBERSHIPS: Dict[str, Dict[str, OrgMembership]] = {
    # user-id: {org-id: OrgMembership}
    "user-cfo-org1": {
        "org-bogdor-01": OrgMembership(organization_id="org-bogdor-01", role=UserRole.CFO),
        "demo-org-fruit": OrgMembership(organization_id="demo-org-fruit", role=UserRole.CFO),
        "scenario-exporter": OrgMembership(organization_id="scenario-exporter", role=UserRole.CFO),
        "org-1": OrgMembership(organization_id="org-1", role=UserRole.CFO),
    },
    "user-accountant-org1": {
        "org-bogdor-01": OrgMembership(organization_id="org-bogdor-01", role=UserRole.CHIEF_ACCOUNTANT),
        "demo-org-fruit": OrgMembership(organization_id="demo-org-fruit", role=UserRole.CHIEF_ACCOUNTANT),
        "demo-org-agro-01": OrgMembership(organization_id="demo-org-agro-01", role=UserRole.CHIEF_ACCOUNTANT),
        "org-test-api-01": OrgMembership(organization_id="org-test-api-01", role=UserRole.CHIEF_ACCOUNTANT),
        "org-test-dup": OrgMembership(organization_id="org-test-dup", role=UserRole.CHIEF_ACCOUNTANT),
        "org-test-commit": OrgMembership(organization_id="org-test-commit", role=UserRole.CHIEF_ACCOUNTANT),
    },
    "user-cfo-org2": {
        "org-zarafshon-02": OrgMembership(organization_id="org-zarafshon-02", role=UserRole.CFO),
        "demo-org-farmer": OrgMembership(organization_id="demo-org-farmer", role=UserRole.CFO),
        "scenario-small-farmer": OrgMembership(organization_id="scenario-small-farmer", role=UserRole.CFO),
        "org-2": OrgMembership(organization_id="org-2", role=UserRole.CFO),
    },
    "user-admin": {
        "org-bogdor-01": OrgMembership(organization_id="org-bogdor-01", role=UserRole.SUPER_ADMIN),
        "org-zarafshon-02": OrgMembership(organization_id="org-zarafshon-02", role=UserRole.SUPER_ADMIN),
    },
    "user-researcher": {
        "org-internal": OrgMembership(organization_id="org-internal", role=UserRole.RESEARCHER),
    },
    "user-demo": {
        "scenario-small-farmer": OrgMembership(organization_id="scenario-small-farmer", role=UserRole.CFO),
        "scenario-exporter": OrgMembership(organization_id="scenario-exporter", role=UserRole.CFO),
        "scenario-cluster": OrgMembership(organization_id="scenario-cluster", role=UserRole.CFO),
        "demo-org-farmer": OrgMembership(organization_id="demo-org-farmer", role=UserRole.CFO),
        "demo-org-fruit": OrgMembership(organization_id="demo-org-fruit", role=UserRole.CFO),
        "demo-org-agro-01": OrgMembership(organization_id="demo-org-agro-01", role=UserRole.CFO),
    },
}


def _b64_url_decode(segment: str) -> bytes:
    """Decodes a base64url encoded string with padding restoration."""
    rem = len(segment) % 4
    if rem > 0:
        segment += "=" * (4 - rem)
    return base64.urlsafe_b64decode(segment.encode("utf-8"))


def _b64_url_encode(data: bytes) -> str:
    """Encodes bytes to a base64url string without trailing padding."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def create_token(
    user_id: str,
    email: str,
    role: UserRole = UserRole.CHIEF_ACCOUNTANT,
    memberships: Optional[Dict[str, str]] = None,
    expires_in_seconds: int = 86400,
    secret: Optional[str] = None
) -> str:
    """Creates a signed HS256 JWT token."""
    key = (secret or settings.SECRET_KEY).encode("utf-8")
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "role": role.value,
        "iat": now,
        "exp": now + expires_in_seconds,
        "app_metadata": {
            "memberships": memberships or {}
        }
    }

    header_b64 = _b64_url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64_url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    sig = hmac.new(key, signing_input, hashlib.sha256).digest()
    sig_b64 = _b64_url_encode(sig)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def verify_token(token: str, secret: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Cryptographically verifies an HS256 JWT token against Supabase / backend secret.
    Validates token format, expiration (exp), and HMAC signature.
    In production environments (ENVIRONMENT=production):
      - Rejects all deterministic test-tokens (test-token-*).
      - Strictly requires a verified cryptographic HMAC signature.
      - Strictly requires an unexpired exp timestamp.
    """
    if not token or not isinstance(token, str):
        return None

    is_production = getattr(settings, "ENVIRONMENT", "development").lower() == "production"

    # Deterministic test/demo tokens are STRICTLY FORBIDDEN in production
    if token.startswith("test-token-"):
        if is_production:
            return None
        token_name = token.replace("test-token-", "")
        if token_name == "cfo-org1":
            return {
                "sub": "user-cfo-org1",
                "email": "cfo@bogdor.uz",
                "role": UserRole.CFO.value,
                "app_metadata": {"memberships": {"org-bogdor-01": "CFO", "demo-org-fruit": "CFO", "scenario-exporter": "CFO", "org-1": "CFO"}}
            }
        elif token_name == "accountant-org1":
            return {
                "sub": "user-accountant-org1",
                "email": "accountant@bogdor.uz",
                "role": UserRole.CHIEF_ACCOUNTANT.value,
                "app_metadata": {"memberships": {"org-bogdor-01": "CHIEF_ACCOUNTANT", "demo-org-fruit": "CHIEF_ACCOUNTANT", "demo-org-agro-01": "CHIEF_ACCOUNTANT", "org-test-api-01": "CHIEF_ACCOUNTANT", "org-test-dup": "CHIEF_ACCOUNTANT", "org-test-commit": "CHIEF_ACCOUNTANT"}}
            }
        elif token_name == "cfo-org2":
            return {
                "sub": "user-cfo-org2",
                "email": "cfo@zarafshon.uz",
                "role": UserRole.CFO.value,
                "app_metadata": {"memberships": {"org-zarafshon-02": "CFO", "demo-org-farmer": "CFO", "scenario-small-farmer": "CFO", "org-2": "CFO"}}
            }
        elif token_name == "admin":
            return {
                "sub": "user-admin",
                "email": "admin@agrohisob.uz",
                "role": UserRole.SUPER_ADMIN.value,
                "app_metadata": {"is_super_admin": True, "memberships": {}}
            }
        elif token_name == "researcher":
            return {
                "sub": "user-researcher",
                "email": "research@agrohisob.uz",
                "role": UserRole.RESEARCHER.value,
                "app_metadata": {"memberships": {"org-internal": "RESEARCHER"}}
            }
        elif token_name == "demo":
            return {
                "sub": "user-demo",
                "email": "demo@agrohisob.uz",
                "role": UserRole.CFO.value,
                "app_metadata": {
                    "memberships": {
                        "scenario-small-farmer": "CFO",
                        "scenario-exporter": "CFO",
                        "scenario-cluster": "CFO",
                        "demo-org-farmer": "CFO",
                        "demo-org-fruit": "CFO",
                        "demo-org-agro-01": "CFO",
                    }
                }
            }
        return None

    parts = token.split(".")
    if len(parts) != 3:
        return None

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    # Determine candidate secrets for HMAC verification
    secrets_to_try = [
        secret,
        getattr(settings, "SUPABASE_JWT_SECRET", None),
        os.getenv("SUPABASE_JWT_SECRET"),
        settings.SECRET_KEY,
    ]
    secrets_to_try = [s for s in secrets_to_try if s]

    verified = False
    for sec in secrets_to_try:
        expected_sig = hmac.new(sec.encode("utf-8"), signing_input, hashlib.sha256).digest()
        expected_sig_b64 = _b64_url_encode(expected_sig)
        if hmac.compare_digest(sig_b64, expected_sig_b64):
            verified = True
            break

    try:
        payload_bytes = _b64_url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return None

    # In production, signature MUST BE VALID. Forged tokens with forged claims are strictly rejected.
    if is_production:
        if not verified:
            return None
        # In production, token MUST have an exp timestamp
        exp = payload.get("exp")
        if not exp or int(time.time()) > exp:
            return None
    else:
        # Non-production mode fallback for dev testing if secrets are not yet mirrored
        if not verified:
            iss = payload.get("iss", "")
            aud = payload.get("aud", "")
            role_claim = payload.get("role", "")
            if ("supabase.co" in iss or "supabase" in iss) and (aud == "authenticated" or role_claim == "authenticated"):
                verified = True
            else:
                return None

        # Expiration check
        exp = payload.get("exp")
        if exp and int(time.time()) > exp:
            return None

    return payload


def load_db_memberships_for_user(user_id: str) -> Dict[str, OrgMembership]:
    """Attempts to query active organization memberships from database for given user_id."""
    try:
        from app.db.database import SessionLocal
        from app.models.core import OrganizationMembership
        session = SessionLocal()
        try:
            records = session.query(OrganizationMembership).filter(
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.is_active == True
            ).all()
            result = {}
            for r in records:
                try:
                    r_enum = UserRole(r.role)
                except ValueError:
                    r_enum = UserRole.CHIEF_ACCOUNTANT
                result[r.organization_id] = OrgMembership(organization_id=r.organization_id, role=r_enum)
            return result
        finally:
            session.close()
    except Exception:
        return {}


def extract_user_from_payload(payload: Dict[str, Any]) -> AuthenticatedUser:
    """Builds an AuthenticatedUser instance with validated memberships from token payload."""
    user_id = payload.get("sub", "anon-user")
    email = payload.get("email", "unknown@agrohisob.uz")
    raw_role = payload.get("role", "CHIEF_ACCOUNTANT")
    is_production = getattr(settings, "ENVIRONMENT", "development").lower() == "production"

    if raw_role == "authenticated":
        role = UserRole.CFO
    else:
        try:
            role = UserRole(raw_role)
        except ValueError:
            role = UserRole.CHIEF_ACCOUNTANT

    is_super_admin = role == UserRole.SUPER_ADMIN or payload.get("app_metadata", {}).get("is_super_admin", False)

    # 1. Resolve memberships explicitly embedded in token payload
    memberships: Dict[str, OrgMembership] = {}
    app_meta_memberships = payload.get("app_metadata", {}).get("memberships", {})
    if isinstance(app_meta_memberships, dict):
        for org_id, r_str in app_meta_memberships.items():
            try:
                r_enum = UserRole(r_str)
            except ValueError:
                r_enum = UserRole.CHIEF_ACCOUNTANT
            memberships[org_id] = OrgMembership(organization_id=org_id, role=r_enum)

    # 2. Check durable PostgreSQL database for active organization memberships
    if not memberships:
        db_memberships = load_db_memberships_for_user(user_id)
        if db_memberships:
            memberships = db_memberships

    # 3. Check registered demo memberships
    if not memberships and user_id in DEMO_MEMBERSHIPS:
        memberships = DEMO_MEMBERSHIPS[user_id]

    # 4. In development/testing/demo only: provision benchmark demo scenarios if user has no assigned org
    if not memberships and not is_production and (raw_role == "authenticated" or role in (UserRole.CFO, UserRole.CHIEF_ACCOUNTANT)):
        memberships = {
            "scenario-small-farmer": OrgMembership(organization_id="scenario-small-farmer", role=UserRole.CFO),
            "scenario-exporter": OrgMembership(organization_id="scenario-exporter", role=UserRole.CFO),
            "scenario-cluster": OrgMembership(organization_id="scenario-cluster", role=UserRole.CFO),
            "demo-org-agro-01": OrgMembership(organization_id="demo-org-agro-01", role=UserRole.CFO),
        }

    return AuthenticatedUser(
        user_id=user_id,
        email=email,
        role=role,
        memberships=memberships,
        is_super_admin=is_super_admin,
    )
