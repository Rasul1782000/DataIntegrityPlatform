"""Shared helper for parsing the GraphQL `orderBy` argument convention.

The frontend passes values such as ``"detectedAt_DESC"`` or ``"createdAt_ASC"``.
Each module maps its exposed GraphQL field names to SQLAlchemy columns and
delegates parsing here so the convention stays consistent everywhere.
"""

from typing import Any

from sqlalchemy.sql.elements import UnaryExpression


def parse_order_by(
    order_by: str | None,
    allowed: dict[str, Any],
    default: str,
) -> UnaryExpression:
    """Return an SQLAlchemy ORDER BY clause for a GraphQL orderBy string.

    Args:
        order_by: Client value like ``"detectedAt_DESC"``. ``None`` or an
            unknown field silently falls back to ``default`` so queries never
            fail because of ordering input.
        allowed: Mapping of camelCase field name -> SQLAlchemy column.
        default: Fallback entry name from ``allowed`` (without suffix).
    """
    name = order_by or f"{default}_DESC"
    field, _, direction = name.partition("_")
    column = allowed.get(field, allowed.get(default))
    descending = direction.casefold() != "asc"
    return column.desc() if descending else column.asc()
