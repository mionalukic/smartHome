import time
import random


def run_kitchen_dht_simulator(stop_event, print_fn=print,
                              mqtt_publisher=None,
                              device_id="pi",
                              component="DHT3",
                              interval=2):

    print_fn("Kitchen DHT simulator started")

    temp = 22.0
    hum = 45.0

    while not stop_event.is_set():
        # mala varijacija
        temp += random.uniform(-0.3, 0.3)
        hum += random.uniform(-1.0, 1.0)

        ts = time.time()
        print_fn(f"DHT TEMP={temp:.1f}°C HUM={hum:.1f}%")

        if mqtt_publisher and mqtt_publisher.connected:
            payload = {
                "device_id": device_id,
                "sensor_type": "kitchen_dht",
                "component": component,
                "temperature": round(temp, 1),
                "humidity": round(hum, 1),
                "simulated": True,
                "timestamp": ts
            }

            topic = f"smarthome/{device_id}/sensors/{component.lower()}"
            mqtt_publisher.publish(topic, payload, use_batch=True)

        time.sleep(interval)

    print_fn("Kitchen DHT simulator stopped")
