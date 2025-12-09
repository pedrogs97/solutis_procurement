"""
Database connection service for external databases.
This module implements the connection logic to SQL Server using Singleton pattern.
"""

import os
from typing import Optional

import pymssql


class DatabaseConnectionService:
    """
    Service for managing external database connections using Singleton pattern.
    Ensures only one connection instance exists throughout the application.
    """

    _instance: Optional["DatabaseConnectionService"] = None
    _connection: Optional[pymssql.Connection] = None

    def __new__(cls):
        """Implement Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the connection service"""
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._cursor = None

    def connect(self) -> pymssql.Connection:
        """
        Establish connection to SQL Server database.

        Returns:
            pymssql.Connection: Active database connection

        Raises:
            pymssql.Error: If connection fails
        """
        if self._connection is None or not self._is_connection_alive():
            self._connection = pymssql.connect(
                server=os.getenv("SQLSERVER_HOST_DB", ""),
                user=os.getenv("SQLSERVER_USER_DB", ""),
                password=os.getenv("SQLSERVER_PASSWORD_DB", ""),
                database=os.getenv("SQLSERVER_NAME_DB", ""),
            )
        return self._connection

    def get_cursor(self, as_dict: bool = True) -> pymssql.Cursor:
        """
        Get database cursor for executing queries.

        Args:
            as_dict: If True, returns results as dictionaries

        Returns:
            pymssql.Cursor: Database cursor
        """
        if self._connection is None:
            self.connect()

        if self._cursor is None or not self._is_connection_alive():
            self._cursor = self._connection.cursor(as_dict=as_dict)

        return self._cursor

    def close(self) -> None:
        """Close database connection and cursor"""
        if self._cursor:
            self._cursor.close()
            self._cursor = None

        if self._connection:
            self._connection.close()
            self._connection = None

    def _is_connection_alive(self) -> bool:
        """
        Check if connection is still alive.

        Returns:
            bool: True if connection is alive, False otherwise
        """
        if self._connection is None:
            return False

        try:
            # Try to execute a simple query to check if connection is alive
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except (pymssql.Error, AttributeError):
            return False

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
