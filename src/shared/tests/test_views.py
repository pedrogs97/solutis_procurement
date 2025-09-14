"""
Tests for shared views.
This module contains tests for BaseAPIView and related view components.
"""

from unittest.mock import Mock

from django.test import TestCase
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from src.shared.models import Contact
from src.shared.views import BaseAPIView


class DummySerializer(serializers.ModelSerializer):
    """Dummy serializer for testing BaseAPIView."""

    class Meta:
        model = Contact
        fields = ["email", "phone"]


class DummyInSerializer(serializers.ModelSerializer):
    """Dummy input serializer for testing BaseAPIView."""

    class Meta:
        model = Contact
        fields = ["email", "phone"]


class DummyOutSerializer(serializers.ModelSerializer):
    """Dummy output serializer for testing BaseAPIView."""

    class Meta:
        model = Contact
        fields = ["id", "email", "phone", "created_at"]


class DummyView(BaseAPIView):
    """Dummy view for testing BaseAPIView functionality."""

    serializer_class = DummySerializer
    queryset = Contact.objects.all()
    format_kwarg = None

    def __init__(self):
        super().__init__()
        self.format_kwarg = None

    # Override methods for testing to avoid relying on request.data
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        data = request.POST
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        new_instance = serializer.save()
        return_data = self.get_out_serializer_class()(new_instance).data
        return Response(return_data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.POST
        serializer = self.get_serializer(instance, data=data)
        serializer.is_valid(raise_exception=True)
        return_data = self.get_out_serializer_class()(serializer.save()).data
        return Response(return_data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.POST
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        return_data = self.get_out_serializer_class()(serializer.save()).data
        return Response(return_data, status=status.HTTP_200_OK)


class DummyViewWithInOut(BaseAPIView):
    """Dummy view with separate input/output serializers."""

    serializer_class_in = DummyInSerializer
    serializer_class_out = DummyOutSerializer
    queryset = Contact.objects.all()
    format_kwarg = None

    def __init__(self):
        super().__init__()
        self.format_kwarg = None

    # Override methods for testing to avoid relying on request.data
    def post(self, request, *args, **kwargs):
        data = request.POST
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        new_instance = serializer.save()
        return_data = self.get_out_serializer_class()(new_instance).data
        return Response(return_data, status=status.HTTP_201_CREATED)


class TestBaseAPIView(TestCase):
    """Test cases for BaseAPIView."""

    def setUp(self):
        """Set up test data."""
        self.factory = APIRequestFactory()
        self.contact = Contact.objects.create(
            email="test@example.com", phone="11999999999"
        )

    def test_get_serializer_class_with_single_serializer(self):
        """Test get_serializer_class with only serializer_class."""
        view = DummyView()
        view.request = Mock()
        view.request.method = "GET"

        self.assertEqual(view.get_serializer_class(), DummySerializer)

    def test_get_serializer_class_with_in_out_serializers_post(self):
        """Test get_serializer_class with POST request using serializer_class_in."""
        view = DummyViewWithInOut()
        view.request = Mock()
        view.request.method = "POST"

        self.assertEqual(view.get_serializer_class(), DummyInSerializer)

    def test_get_serializer_class_with_in_out_serializers_get(self):
        """Test get_serializer_class with GET request using serializer_class_out."""
        view = DummyViewWithInOut()
        view.request = Mock()
        view.request.method = "GET"

        self.assertEqual(view.get_serializer_class(), DummyOutSerializer)

    def test_get_serializer_class_assertion_error(self):
        """Test get_serializer_class raises assertion error when no serializer is defined."""

        class EmptyView(BaseAPIView):
            pass

        view = EmptyView()
        view.request = Mock()
        view.request.method = "GET"

        with self.assertRaises(AssertionError):
            view.get_serializer_class()

    def test_get_out_serializer_class(self):
        """Test get_out_serializer_class method."""
        view = DummyViewWithInOut()
        self.assertEqual(view.get_out_serializer_class(), DummyOutSerializer)

        # Test fallback to serializer_class
        view_single = DummyView()
        self.assertEqual(view_single.get_out_serializer_class(), DummySerializer)

    def test_get_request(self):
        """Test GET request handling."""
        view = DummyView()
        view.get_object = Mock(return_value=self.contact)

        request = self.factory.get("/test/")
        view.request = request

        response = view.get(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("email", response.data)

    def test_post_request(self):
        """Test POST request handling."""
        view = DummyView()

        data = {"email": "new@example.com", "phone": "11888888888"}
        request = self.factory.post("/test/", data)
        view.request = request

        response = view.post(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("email", response.data)

    def test_put_request(self):
        """Test PUT request handling."""
        view = DummyView()
        view.get_object = Mock(return_value=self.contact)

        data = {"email": "updated@example.com", "phone": "11777777777"}
        request = self.factory.put("/test/", data)
        view.request = request

        response = view.put(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_request(self):
        """Test PATCH request handling."""
        view = DummyView()
        view.get_object = Mock(return_value=self.contact)

        data = {"phone": "11666666666"}
        request = self.factory.patch("/test/", data)
        view.request = request

        response = view.patch(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_request(self):
        """Test DELETE request handling."""
        view = DummyView()
        mock_instance = Mock()
        view.get_object = Mock(return_value=mock_instance)

        request = self.factory.delete("/test/")
        view.request = request

        response = view.delete(request)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_instance.delete.assert_called_once()

    def test_post_with_in_out_serializers(self):
        """Test POST request with separate input/output serializers."""
        view = DummyViewWithInOut()

        data = {"email": "test@example.com", "phone": "11555555555"}
        request = self.factory.post("/test/", data)
        view.request = request

        response = view.post(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Should use output serializer for response
        self.assertIn("created_at", response.data)

    def test_method_routing(self):
        """Test that different HTTP methods use appropriate serializers."""
        view = DummyViewWithInOut()

        # Test POST uses input serializer
        view.request = Mock()
        view.request.method = "POST"
        self.assertEqual(view.get_serializer_class(), DummyInSerializer)

        # Test PUT uses input serializer
        view.request.method = "PUT"
        self.assertEqual(view.get_serializer_class(), DummyInSerializer)

        # Test PATCH uses input serializer
        view.request.method = "PATCH"
        self.assertEqual(view.get_serializer_class(), DummyInSerializer)

        # Test GET uses output serializer
        view.request.method = "GET"
        self.assertEqual(view.get_serializer_class(), DummyOutSerializer)

        # Test HEAD uses output serializer
        view.request.method = "HEAD"
        self.assertEqual(view.get_serializer_class(), DummyOutSerializer)

        # Test OPTIONS uses output serializer
        view.request.method = "OPTIONS"
        self.assertEqual(view.get_serializer_class(), DummyOutSerializer)

    def test_serializer_class_priority(self):
        """Test serializer class priority when multiple are defined."""

        class ViewWithAll(BaseAPIView):
            serializer_class = DummySerializer
            serializer_class_in = DummyInSerializer
            serializer_class_out = DummyOutSerializer

        view = ViewWithAll()
        view.request = Mock()

        # POST should use serializer_class_in
        view.request.method = "POST"
        self.assertEqual(view.get_serializer_class(), DummyInSerializer)

        # GET should use serializer_class_out
        view.request.method = "GET"
        self.assertEqual(view.get_serializer_class(), DummyOutSerializer)

    def test_fallback_to_serializer_class(self):
        """Test fallback to serializer_class when in/out not defined."""

        class ViewWithOnlyBase(BaseAPIView):
            serializer_class = DummySerializer

        view = ViewWithOnlyBase()
        view.request = Mock()

        # All methods should use base serializer_class
        for method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            view.request.method = method
            self.assertEqual(view.get_serializer_class(), DummySerializer)
