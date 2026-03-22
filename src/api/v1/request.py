"""Request helpers for Ninja v1."""

import json

from src.utils.parse import to_snake_case


def get_request_data(request):
    """Read request payload in a format compatible with DRF serializers."""
    content_type = (request.content_type or "").lower()

    if content_type.startswith("application/json"):
        if not request.body:
            return {}
        return json.loads(request.body.decode("utf-8"))

    data = request.POST.copy()
    parsed = {to_snake_case(key): value for key, value in data.items()}
    for key, value in request.FILES.items():
        parsed[to_snake_case(key)] = value
    return parsed
