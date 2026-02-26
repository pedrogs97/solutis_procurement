"""Tests for proxy-header authentication backend used by procurement APIs."""

from django.test import RequestFactory, SimpleTestCase
from rest_framework.exceptions import AuthenticationFailed

from src.shared.authentication import ProxyHeaderAuthentication


class TestProxyHeaderAuthentication(SimpleTestCase):
    """Unit tests for proxy-header authentication backend."""

    def setUp(self):
        self.factory = RequestFactory()
        self.authentication = ProxyHeaderAuthentication()

    def test_authenticate_reads_identity_from_proxy_headers(self):
        request = self.factory.get(
            "/api/suppliers/",
            HTTP_AUTHORIZATION="Bearer opaque-token",
            HTTP_X_AUTHENTICATED_USER_ID="12",
            HTTP_X_AUTHENTICATED_USER_EMAIL="proxy.user@solutis.com.br",
            HTTP_X_AUTHENTICATED_USER_FULL_NAME="Proxy User",
            HTTP_X_AUTHENTICATED_USER_GROUP="Compras",
        )

        user, auth_context = self.authentication.authenticate(request)

        self.assertEqual(user.id, 12)
        self.assertEqual(user.email, "proxy.user@solutis.com.br")
        self.assertEqual(user.full_name, "Proxy User")
        self.assertEqual(user.group, "Compras")
        self.assertEqual(auth_context["id"], 12)

    def test_authenticate_requires_identity_claims(self):
        request = self.factory.get(
            "/api/suppliers/",
            HTTP_AUTHORIZATION="Bearer opaque-token",
            HTTP_X_AUTHENTICATED_USER_ID="12",
            HTTP_X_AUTHENTICATED_USER_EMAIL="",
            HTTP_X_AUTHENTICATED_USER_FULL_NAME="Proxy User",
            HTTP_X_AUTHENTICATED_USER_GROUP="Compras",
        )

        with self.assertRaises(AuthenticationFailed):
            self.authentication.authenticate(request)
