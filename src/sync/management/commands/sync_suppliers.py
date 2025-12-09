"""
Management command to synchronize suppliers from TOTVS.
Usage: python manage.py sync_suppliers
"""

from django.core.management.base import BaseCommand

from src.sync.services import DatabaseConnectionService, SupplierSyncService


class Command(BaseCommand):
    """Django management command for syncing suppliers from TOTVS"""

    help = "Synchronize suppliers from TOTVS to local database"

    def handle(self, *args, **options):
        """Execute the command"""
        self.stdout.write(self.style.WARNING("Starting supplier synchronization..."))

        try:
            # Initialize services
            db_service = DatabaseConnectionService()
            sync_service = SupplierSyncService(db_service)

            # Execute synchronization
            count = sync_service.sync_suppliers()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully synchronized {count} suppliers from TOTVS"
                )
            )

        except Exception as error:
            self.stdout.write(
                self.style.ERROR(f"Failed to synchronize suppliers: {error}")
            )
            raise
