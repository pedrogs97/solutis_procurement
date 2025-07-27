"""
Custom pagination classes for the procurement service.
This module provides customized pagination configurations.
"""

from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that uses 'size' as the query parameter for page size.
    """

    page_size = 12
    page_size_query_param = "size"
    max_page_size = 100
