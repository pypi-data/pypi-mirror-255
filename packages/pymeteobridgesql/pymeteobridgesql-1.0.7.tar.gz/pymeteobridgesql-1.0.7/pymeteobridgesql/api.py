"""This module contains the code to get weather data from an MYSQL Table."""
from __future__ import annotations

import logging
import mysql.connector

from .data import RealtimeData, StationData

_LOGGER = logging.getLogger(__name__)

class MeteobridgeSQLDatabaseConnectionError(Exception):
    """Cannot connect to database."""


class MeteobridgeSQLDataError(Exception):
    """Cannot lookup data in the database."""


class MeteobridgeSQL:
    """Class that interfaces with a MySQL database, with weather data supplied by Meteobridge."""

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        port: int = 3306,
    ) -> None:
        """Initialize the connection."""
        self._host = host
        self._user = user
        self._password = password
        self._database = database
        self._port = port

        self._weatherdb = None
        self._weather_cursor = None

    async def async_init(self) -> None:
        """Initialize the connection."""
        try:
            self._weatherdb = mysql.connector.connect(
                host=self._host,
                user=self._user,
                password=self._password,
                database=self._database,
                port=self._port,
            )
        except mysql.connector.Error as err:
            raise MeteobridgeSQLDatabaseConnectionError(f"Failed to connect to the database: {err.msg}")

        self._weather_cursor = self._weatherdb.cursor()

    async def async_get_realtime_data(self, id: str) -> RealtimeData:
        """Get the latest data from the database."""

        try:
            self._weather_cursor.execute(
                f"SELECT * FROM realtime_data WHERE ID = '{id}'"
            )
            result = self._weather_cursor.fetchone()
        except mysql.connector.Error as err:
            raise MeteobridgeSQLDataError(f"Failed to lookup data in the database: {err.msg}")

        return RealtimeData(*result)

    async def async_get_station_data(self, id: str) -> RealtimeData:
        """Get station data from the database."""

        try:
            self._weather_cursor.execute(
                f"SELECT ID, mb_ip, mb_swversion, mb_buildnum, mb_platform, mb_station, mb_stationname FROM realtime_data WHERE ID = '{id}'"
            )
            result = self._weather_cursor.fetchone()
        except mysql.connector.Error as err:
            raise MeteobridgeSQLDataError(f"Failed to lookup data in the database: {err.msg}")

        return StationData(*result)


