from enum import StrEnum


class UserRole(StrEnum):
    ADMINISTRATOR = "ADMINISTRATOR"
    SECURITY_ANALYST = "SECURITY_ANALYST"
    AUDITOR = "AUDITOR"
    VIEWER = "VIEWER"


class Permission(StrEnum):
    MANAGE_USERS = "manage_users"
    MANAGE_MONITORING = "manage_monitoring"
    INVESTIGATE_EVENTS = "investigate_events"
    VIEW_AUDIT = "view_audit"
    VIEW_DASHBOARD = "view_dashboard"


ROLE_PERMISSIONS: dict[UserRole, frozenset[Permission]] = {
    UserRole.ADMINISTRATOR: frozenset(Permission),
    UserRole.SECURITY_ANALYST: frozenset(
        {
            Permission.INVESTIGATE_EVENTS,
            Permission.VIEW_DASHBOARD,
        }
    ),
    UserRole.AUDITOR: frozenset({Permission.VIEW_AUDIT, Permission.VIEW_DASHBOARD}),
    UserRole.VIEWER: frozenset({Permission.VIEW_DASHBOARD}),
}


def has_permission(role: UserRole, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS[role]
