"""Authentication backends for procurement APIs."""

from dataclasses import dataclass
from urllib.parse import unquote

from rest_framework.authentication import (BaseAuthentication,
                                           get_authorization_header)
from rest_framework.exceptions import AuthenticationFailed


@dataclass
class ProxyAuthenticatedUser:
    """Authenticated user shape used for proxied requests."""

    id: int
    email: str = ""
    full_name: str = ""
    group: str = ""

    @property
    def is_authenticated(self) -> bool:
        return True

    def get_full_name(self) -> str:
        return self.full_name


class ProxyHeaderAuthentication(BaseAuthentication):
    """
    Validate authenticated headers injected by manager proxy.

    If no Authorization header is provided, this backend returns None so views
    can still opt into public access with `AllowAny`.
    """

    keyword = "bearer"

    def authenticate_header(self, request):
        return "Bearer"

    def authenticate(self, request):
        auth_header = get_authorization_header(request).split()
        if not auth_header:
            return None

        if auth_header[0].lower() != self.keyword.encode():
            return None

        if len(auth_header) != 2:
            raise AuthenticationFailed("Invalid authorization header.")

        context_user_id = request.headers.get("X-Authenticated-User-Id", "")
        try:
            parsed_user_id = int(context_user_id)
        except (TypeError, ValueError) as exc:
            raise AuthenticationFailed("Invalid token payload.") from exc

        email = unquote(
            str(request.headers.get("X-Authenticated-User-Email", "") or "").strip()
        )
        full_name = unquote(
            str(
                request.headers.get("X-Authenticated-User-Full-Name", "") or ""
            ).strip()
        )
        group = unquote(
            str(request.headers.get("X-Authenticated-User-Group", "") or "").strip()
        )

        if not email or not full_name or not group:
            raise AuthenticationFailed("Invalid token payload.")

        user = ProxyAuthenticatedUser(
            id=parsed_user_id,
            email=email,
            full_name=full_name,
            group=group,
        )
        return (user, {"id": parsed_user_id})
