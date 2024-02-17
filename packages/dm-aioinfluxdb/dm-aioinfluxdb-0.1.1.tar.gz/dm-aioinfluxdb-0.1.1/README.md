# DM-aioinfluxdb

## Urls

* [PyPI](https://pypi.org/project/dm-aioinfluxdb)
* [GitHub](https://github.com/DIMKA4621/dm-aioinfluxdb)

## Usage

### Example

```python
from dm_aioinfluxdb import DMAioInfluxDBClient
import asyncio


async def main():
    # create client
    influxdb_client = DMAioInfluxDBClient("localhost", 8086, "org", "token")

    # create influxdb points
    point1 = influxdb_client.create_point("example-measurement", {"value": 1.5}, {"tag1": "tag1-value"})
    point2 = DMAioInfluxDBClient.create_point("example-measurement", {"value": 0}, {"tag2": "tag2-value"})

    # write one or more points
    await influxdb_client.write("example-bucket", point1)
    await influxdb_client.write("example-bucket", [point1, point2])

if __name__ == "__main__":
    asyncio.run(main())
```

### Set custom logger

_If you want set up custom logger_

```python
from dm_aioinfluxdb import DMAioInfluxDBClient


# create custom logger
class MyLogger:
    def debug(self, message):
        pass

    def info(self, message):
        pass

    def warning(self, message):
        print(message)

    def error(self, message):
        print(message)


# set up custom logger for all clients
DMAioInfluxDBClient.set_logger(MyLogger())
```
