"""Django management command: export OpenAPI schema from Django Ninja."""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.test import Client


class Command(BaseCommand):
    help = "Export the Django Ninja OpenAPI schema to a JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="../solutis-agile-frontend/openapi/openapi.json",
            help=(
                "Destination file path. "
                "Default: ../solutis-agile-frontend/openapi/openapi.json"
            ),
        )
        parser.add_argument(
            "--path",
            default="/api/v1/openapi.json",
            help="OpenAPI endpoint exposed by Django Ninja. Default: /api/v1/openapi.json",
        )

    def handle(self, *args, **options):
        endpoint = options["path"]
        output_path = Path(options["output"]).resolve()

        self.stdout.write(f"Fetching OpenAPI schema from {endpoint}...")

        response = Client().get(endpoint)
        if response.status_code != 200:
            self.stderr.write(
                self.style.ERROR(
                    f"Failed: GET {endpoint} returned {response.status_code}"
                )
            )
            raise SystemExit(1)

        content = json.dumps(response.json(), ensure_ascii=False, indent=2) + "\n"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

        self.stdout.write(self.style.SUCCESS(f"OpenAPI schema written to {output_path}"))
