from __future__ import annotations
from dm_logger import DMLogger
from typing import Callable, Literal
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client import Point
import time
import json


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

    async def __connect_handler(self, callback: Callable):
        try:
            async with InfluxDBClientAsync(**self.__influxdb_config) as client:
                return await callback(client)
        except InfluxDBError as e:
            if e.response.status == 401:
                self.__logger.error(f"Insufficient write permissions to bucket: {e.message}")
            else:
                self.__logger.error(f"InfluxDB error: {e.message}")
        except Exception as e:
            self.__logger.error(f"Error: {e}")

    async def write(self, bucket: str, record: Point | list[Point]) -> bool:
        points = record if isinstance(record, list) else [record]
        to_line_points = map(lambda p: p.to_line_protocol(), points)
        points = list(filter(lambda p: p, to_line_points))
        if not points:
            return False

        async def write_callback(client: InfluxDBClientAsync):
            await client.write_api().write(bucket=bucket, record=points)
            return True

        return await self.__connect_handler(write_callback)

    async def query(self, query: str, to: Literal["json", "dict"] | None = None) -> list:

        async def query_callback(client: InfluxDBClientAsync):
            q_result = await client.query_api().query(query=query)

            if to is not None:
                result = q_result.to_json()
                if to == "dict":
                    result = json.loads(result)
            else:
                result = q_result
            return result

        return await self.__connect_handler(query_callback)

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
