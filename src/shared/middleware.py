"""
Middleware for the shared app in Django.
"""

import json

from django.utils.deprecation import MiddlewareMixin

from src.utils.parse import to_snake_case


class SnakeCaseMiddleware(MiddlewareMixin):
    """
    Middleware to convert request data keys to snake_case.
    This is useful for ensuring consistent naming conventions in APIs.
    """

    def __dict_to_snake_case(self, data: dict) -> dict:
        dict_data = {}
        for k, v in data.items():
            if isinstance(v, dict):
                dict_data[to_snake_case(k)] = self.__dict_to_snake_case(v)
            elif isinstance(v, list):
                dict_data[to_snake_case(k)] = [
                    self.__dict_to_snake_case(item) if isinstance(item, dict) else item
                    for item in v
                ]
            else:
                dict_data[to_snake_case(k)] = v
        return dict_data

    def process_request(self, request):
        if (
            request.method in ["POST", "PUT", "PATCH"]
            and request.content_type == "application/json"
        ):
            body = request.body.decode("utf-8")
            data = json.loads(body)
            snake_case_data = self.__dict_to_snake_case(data)
            request._body = json.dumps(snake_case_data).encode("utf-8")
            request._data = snake_case_data
