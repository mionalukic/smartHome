import time
import random


def run_ultrasonic_simulator(stop_event, print_fn=print,
                             mqtt_publisher=None, device_id='pi',
                             component='DUS'):

    distance = random.randint(80, 140)
    print_fn(f"Ultrasonic simulator {component} started")

    while not stop_event.is_set():
        distance += random.randint(-3, 3)
        distance = max(10, min(200, distance))
        ts = time.time()

        print_fn(f"{component} Distance: {distance} cm")

        if mqtt_publisher and mqtt_publisher.connected:
            payload = {
                "device_id": device_id,
                "sensor_type": "ultrasonic_sensor",
                "component": component,
                "distance_cm": distance,
                "unit": "cm",
                "simulated": True,
                "timestamp": ts
            }

            topic = f"smarthome/{device_id}/sensors/{component.lower()}"
            mqtt_publisher.publish(topic, payload, use_batch=True)

        time.sleep(1)

    print_fn(f"Ultrasonic simulator {component} stopped")
