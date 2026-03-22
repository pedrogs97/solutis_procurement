"""Authentication adapters for Ninja v1 API."""

from ninja.errors import HttpError
from ninja.security import HttpBearer
from rest_framework.exceptions import AuthenticationFailed

from src.shared.authentication import ProxyHeaderAuthentication


class ProxyHeaderBearerAuth(HttpBearer):
    """Ninja auth backend compatible with proxy header authentication."""

    def __init__(self):
        super().__init__()
        self.backend = ProxyHeaderAuthentication()

    def authenticate(self, request, token):
        try:
            auth_result = self.backend.authenticate(request)
        except AuthenticationFailed as exc:
            raise HttpError(401, str(exc)) from exc

        if not auth_result:
            return None

        user, auth_context = auth_result
        request.user = user
        request.auth = auth_context
        return user
