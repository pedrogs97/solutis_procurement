"""Shared schemas for the project."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    """Paginated list response."""

    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[Dict[str, Any]]
