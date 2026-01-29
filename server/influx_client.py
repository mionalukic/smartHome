from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET

client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = client.write_api(write_options=SYNCHRONOUS)


def write_sensor_data(payload: dict):
    
    point = (
        Point("sensor_data")
        .tag("device_id", payload.get("device_id", "unknown"))
        .tag("sensor_type", payload.get("sensor_type", "unknown"))
        .tag("component", payload.get("component", "unknown"))
    )

    for key, value in payload.items():
        if isinstance(value, (int, float)):
            point = point.field(key, value)
        elif isinstance(value, bool):
            point = point.field(key, int(value))

    write_api.write(bucket=INFLUX_BUCKET, record=point)
