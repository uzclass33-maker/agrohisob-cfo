"""
AgroHisob CFO - Security & Tenant Authorization Dependencies
Enforces server-side authentication, role-based access control, and cross-tenant data isolation.
"""

from typing import Callable, Optional
from fastapi import Depends, Header, HTTPException, Request, status
from app.auth.models import AuthenticatedUser, UserRole
from app.auth.security import extract_user_from_payload, verify_token


def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> AuthenticatedUser:
    """
    Extracts and cryptographically validates the Bearer token from the Authorization header.
    Rejects any unauthenticated or tampered request with HTTP 401 Unauthorized.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentifikatsiya talab etiladi: 'Authorization: Bearer <token>' sarlavhasi taqdim etilmagan.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Noto'g'ri autentifikatsiya formati. Format: 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yaroqsiz yoki muddati o'tgan token. Iltimos, qayta tizimga kiring.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return extract_user_from_payload(payload)


def get_optional_current_user(
    request: Request,
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[AuthenticatedUser]:
    """Extracts authenticated user if token is present and valid; returns None otherwise."""
    if not authorization:
        return None
    try:
        return get_current_user(request=request, authorization=authorization)
    except HTTPException:
        return None


def verify_tenant_access(
    requested_org_id: str,
    user: AuthenticatedUser,
    min_role: Optional[UserRole] = None,
) -> None:
    """
    Authoritative server-side tenant isolation check.
    Guarantees that the client-supplied organization_id is NEVER trusted blindly:
    it must strictly match a valid, verified membership in the authenticated user's session.
    """
    # Demo synthetic orgs allow read access in non-production, but never cross-org mutation
    if user.is_super_admin:
        return

    if not user.has_org_access(requested_org_id, min_role=min_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Tashkilotlararo ruxsat rad etildi: Foydalanuvchi '{user.email}' tashkilot '{requested_org_id}' ma'lumotlariga kirish huquqiga ega emas.",
        )


def require_admin_or_researcher(
    user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """Restricts endpoint access to administrators or authorized researchers."""
    if user.is_super_admin or user.role in (UserRole.SUPER_ADMIN, UserRole.RESEARCHER):
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Ruxsat berilmagan: Ushbu resurs faqat tizim administratori yoki tadqiqotchi roli uchun ochiq.",
    )


def require_admin(
    user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    """Restricts endpoint access strictly to Super Administrators."""
    if user.is_super_admin or user.role == UserRole.SUPER_ADMIN:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Ruxsat berilmagan: Ushbu operatsiya faqat tizim administratori uchun ruxsat etilgan.",
    )
