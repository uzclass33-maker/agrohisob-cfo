"""
AgroHisob CFO - Core Security & Authentication Models
Defines user identity, roles, organization memberships, and JWT token payloads.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    CFO = "CFO"
    CHIEF_ACCOUNTANT = "CHIEF_ACCOUNTANT"
    FINANCIAL_ANALYST = "FINANCIAL_ANALYST"
    BANK_AUDITOR = "BANK_AUDITOR"
    RESEARCHER = "RESEARCHER"
    VIEWER = "VIEWER"


class OrgMembership(BaseModel):
    organization_id: str
    role: UserRole
    is_active: bool = True


class AuthenticatedUser(BaseModel):
    user_id: str
    email: str
    role: UserRole
    memberships: Dict[str, OrgMembership] = Field(default_factory=dict)
    is_super_admin: bool = False

    def has_org_access(self, org_id: str, min_role: Optional[UserRole] = None) -> bool:
        if self.is_super_admin:
            return True
        membership = self.memberships.get(org_id)
        if not membership or not membership.is_active:
            return False
        if min_role is None:
            return True
        # Hierarchy: SUPER_ADMIN > CFO > CHIEF_ACCOUNTANT > FINANCIAL_ANALYST > VIEWER
        hierarchy = [
            UserRole.VIEWER,
            UserRole.FINANCIAL_ANALYST,
            UserRole.CHIEF_ACCOUNTANT,
            UserRole.CFO,
            UserRole.SUPER_ADMIN,
        ]
        try:
            user_idx = hierarchy.index(membership.role)
            req_idx = hierarchy.index(min_role)
            return user_idx >= req_idx
        except ValueError:
            return membership.role == min_role
