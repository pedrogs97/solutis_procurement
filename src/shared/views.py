"""
Base API view for shared functionality in Django applications.
This module provides a base view that can be extended for specific functionalities.
"""

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class BaseAPIView(GenericAPIView):
    """
    Base API view that can be extended for specific functionalities.
    Provides common methods for handling requests.
    """

    serializer_class = None
    serializer_class_in = None
    serializer_class_out = None

    def get_serializer_class(self):
        """
        Determine the serializer class to use based on the request method.
        If `serializer_class_in` is provided, it will be used for POST, PUT, and PATCH requests.
        If `serializer_class_out` is provided, it will be used for GET, HEAD, and OPTIONS requests.
        If neither is provided, it will fall back to `serializer_class`.
        """
        if not self.serializer_class_out and not self.serializer_class_in:
            assert self.serializer_class is not None, (
                f"'{self.__class__.__name__}' should include a `serializer_class` attribute when "
                "`serializer_class_in` and `serializer_class_out` are not provided."
            )
            return self.serializer_class

        if (
            self.serializer_class_in
            and self.request.method
            and self.request.method.upper() in ["POST", "PUT", "PATCH"]
        ):
            return self.serializer_class_in

        if (
            self.serializer_class_out
            and self.request.method
            and self.request.method.upper() in ["GET", "HEAD", "OPTIONS"]
        ):
            return self.serializer_class_out

        if self.serializer_class:
            return self.serializer_class

        raise AssertionError(
            f"'{self.__class__.__name__}' must define either `serializer_class`, or both "
            "`serializer_class_in` and `serializer_class_out` attributes."
        )

    def get_out_serializer_class(self):
        """
        Get the serializer class for output serialization.
        This is used for GET, HEAD, and OPTIONS requests.
        """
        return self.serializer_class_out or self.serializer_class

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to retrieve an object.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to create a new object.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_instance = serializer.save()
        return_data = self.get_out_serializer_class()(new_instance).data
        return Response(return_data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        """
        Handle PUT requests to update an existing object.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        return_data = self.get_out_serializer_class()(serializer.save()).data
        return Response(return_data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        Handle PATCH requests to partially update an existing object.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return_data = self.get_out_serializer_class()(serializer.save()).data
        return Response(return_data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """
        Handle DELETE requests to delete an object.
        """
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
