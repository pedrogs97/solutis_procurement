"""Ninja API v1 setup."""

from ninja import NinjaAPI

from src.api.v1.auth import ProxyHeaderBearerAuth
from src.api.v1.exceptions import register_exception_handlers
from src.api.v1.routers.approval import router as approval_router
from src.api.v1.routers.attachments import router as attachments_router
from src.api.v1.routers.responsibility_matrix import (
    router as responsibility_matrix_router,
)
from src.api.v1.routers.suppliers import router as suppliers_router

api_v1 = NinjaAPI(
    title="Solutis Procurement API",
    version="1.0.0",
    auth=ProxyHeaderBearerAuth(),
    urls_namespace="api-1.0.0",
)

api_v1.add_router("", suppliers_router)
api_v1.add_router("", attachments_router)
api_v1.add_router("", responsibility_matrix_router)
api_v1.add_router("/approval", approval_router)

register_exception_handlers(api_v1)
