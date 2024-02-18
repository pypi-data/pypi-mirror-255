from __future__ import annotations
from dm_logger import DMLogger
from typing import Callable, Literal
from influxdb_client.client.influxdb_client_async import InfluxDBClientAsync
from influxdb_client.client.exceptions import InfluxDBError
from influxdb_client.client.flux_table import TableList
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

    async def __execute(
        self,
        callback: Callable,
        return_errors: bool = False,
        err_logging: bool = True
    ):
        return_errors = return_errors if return_errors is not None else False
        err_logging = err_logging if err_logging is not None else True
        error_message = ""
        result = None

        try:
            async with InfluxDBClientAsync(**self.__influxdb_config) as client:
                result = await callback(client)
        except InfluxDBError as e:
            if e.response.status == 401:
                error_message = f"Insufficient write permissions to bucket: {e.message}"
            else:
                error_message = f"InfluxDB error: {e.message}"
        except Exception as e:
            error_message = f"Error: {e}"

        if err_logging and error_message:
            self.__logger.error(error_message)
        if return_errors:
            return result, error_message
        return result

    async def write(
        self,
        bucket: str,
        record: Point | list[Point],
        return_errors: bool = None,
        err_logging: bool = None
    ) -> bool | (bool, str):
        points = record if isinstance(record, list) else [record]
        to_line_points = map(lambda p: p.to_line_protocol(), points)
        points = list(filter(lambda p: p, to_line_points))
        if not points:
            return False

        async def write_callback(client: InfluxDBClientAsync) -> bool:
            await client.write_api().write(bucket=bucket, record=points)
            return True

        return await self.__execute(write_callback, return_errors, err_logging)

    async def query(
        self,
        query: str,
        to: Literal["json", "list"] | None = None,
        return_errors: bool = None,
        err_logging: bool = None
    ) -> TableList | None | str | list[dict] | (TableList, str) | (None, str) | (str, str) | (list[dict], str):

        async def query_callback(client: InfluxDBClientAsync) -> TableList | None:
            return await client.query_api().query(query=query)

        e_result = await self.__execute(query_callback, return_errors, err_logging)
        if return_errors:
            e_result, error_message = e_result

        if to in ("json", "list"):
            if e_result is None:
                if to == "json":
                    result = "null"
                else:
                    result = []
            else:
                result = e_result.to_json()
                result = json.loads(result)
                if to == "json":
                    result = json.dumps(result, ensure_ascii=False)
        else:
            result = e_result

        if return_errors:
            result = (result, error_message)
        return result

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
