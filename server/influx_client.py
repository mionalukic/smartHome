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
    measurement = payload.get("sensor_type", "unknown")

    point = (
        Point(measurement)
        .tag("device_id", payload.get("device_id", "unknown"))
        .tag("component", payload.get("component", "unknown"))
        .tag("simulated", str(payload.get("simulated", False)))
        .tag("topic", payload.get("_topic", "unknown"))
    )


    if measurement in ("door_sensor", "door_motion_sensor"):
        point = point.field("value", int(payload.get("value", 0)))

    elif measurement == "ultrasonic_sensor":
        point = point.field("distance", float(payload["distance_cm"]))


    elif measurement == "door_membrane_switch":
        try:
            key_value = int(payload.get("key", -1))
            point = point.field("key", key_value)
        except ValueError:
            return
    elif measurement == "door_light":
        point = point.field("value", int(payload.get("value", 0)))

    elif measurement == "door_buzzer":
        # Ako postoji pitch ili duration → buzzer je bio aktivan
        active = 1 if ("pitch" in payload or "duration" in payload) else 0
        point = point.field("value", active)




    write_api.write(bucket=INFLUX_BUCKET, record=point)

