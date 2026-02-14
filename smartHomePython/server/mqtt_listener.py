import json
import paho.mqtt.client as mqtt
from influx_client import write_sensor_data
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC


def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected")
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"[MQTT] {msg.topic} -> {payload}")
        write_sensor_data(payload)
    except Exception as e:
        print(f"[ERROR] {e}")


def start_mqtt_listener():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
