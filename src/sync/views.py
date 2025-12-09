"""
Views for sync operations.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from src.sync.services import DatabaseConnectionService, SupplierSyncService


class SupplierSyncView(APIView):
    """
    API view for triggering supplier synchronization from TOTVS.
    """

    def post(self, request):
        """
        Trigger supplier synchronization.

        Returns:
            Response: JSON response with synchronization results
        """
        try:
            db_service = DatabaseConnectionService()
            sync_service = SupplierSyncService(db_service)

            count = sync_service.sync_suppliers()

            return Response(
                {
                    "message": "Suppliers synchronized successfully",
                    "count": count,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as error:
            return Response(
                {
                    "error": "Failed to synchronize suppliers",
                    "details": str(error),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
