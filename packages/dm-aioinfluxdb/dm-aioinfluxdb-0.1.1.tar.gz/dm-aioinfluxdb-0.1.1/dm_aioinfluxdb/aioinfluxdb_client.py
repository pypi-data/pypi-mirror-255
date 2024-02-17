from __future__ import annotations
from dm_logger import DMLogger
from typing import Callable
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client import Point
import asyncio
import time


class DMAioInfluxDBClient:
    __logger = None

    def __init__(self, host: str, port: int, org: str, token: str, *, record_failed_points: bool = True) -> None:
        if self.__logger is None:
            self.__logger = DMLogger(f"{self.__class__.__name__}-{host}:{port}")

        self.__influxdb_config = {
            "url": f"http://{host}:{port}",
            "org": org,
            "token": token
        }
        self.__org = org
        self.__record_failed_points = record_failed_points
        self.__unrecorded_points = []

    @staticmethod
    def create_point(
        measurement: str,
        fields: dict[str, str | int | float],
        tags: dict[str, str] | None = None,
        time_stamp: int | None = None,  # UNIX time stamp
    ) -> Point:
        if time_stamp is not None:
            time_stamp = int(str(time_stamp).ljust(19, "0"))
        point = Point(measurement).time(time_stamp or int(time.time_ns()))
        for k, v in fields.items():
            point.field(k, v)
        if tags:
            for k, v in tags.items():
                point.tag(k, v)
        return point

    async def write(self, bucket: str, record: Point | list[Point]) -> bool:
        points = record if isinstance(record, list) else [record]
        to_line_points = map(lambda p: p.to_line_protocol(), points)
        points = list(filter(lambda p: p, to_line_points))
        if not points:
            return False

        points.extend(self.__unrecorded_points)
        invalid_value_type = False
        try:
            async with InfluxDBClientAsync(**self.__influxdb_config) as client:
                await client.write_api().write(bucket=bucket, record=points)
        except InfluxDBError as e:
            if e.response.status == 401:
                err_mes = f"Insufficient write permissions to '{bucket}' bucket: {e.message}"
            else:
                err_mes = f"InfluxDB write error: {e.message}"
                invalid_value_type = "field type conflict" in e.message
        except asyncio.exceptions.TimeoutError:
            err_mes = f"Error: asyncio.exceptions.TimeoutError: Host connection timed out"
        except Exception as e:
            err_mes = f"Error: {e}"
        else:
            return True

        self.__logger.warning(err_mes)
        if self.__record_failed_points and not invalid_value_type:
            self.__unrecorded_points = points
        return False

    @classmethod
    def set_logger(cls, logger) -> None:
        if (hasattr(logger, "debug") and isinstance(logger.debug, Callable) and
            hasattr(logger, "info") and isinstance(logger.info, Callable) and
            hasattr(logger, "warning") and isinstance(logger.warning, Callable) and
            hasattr(logger, "error") and isinstance(logger.error, Callable)
        ):
            cls.__logger = logger
        else:
            print("Invalid logger")
