import time
import random


def run_dpir_simulator(stop_event, print_fn=print,
                       mqtt_publisher=None, device_id='pi',
                       component='DPIR'):

    print_fn(f"{component} simulator started")

    while not stop_event.is_set():
        duration = random.randint(3, 5)

        ts = time.time()
        print_fn(f"{component} Detected movement")

        if mqtt_publisher and mqtt_publisher.connected:
            payload = {
                "device_id": device_id,
                "sensor_type": "door_motion_sensor",
                "component": component,
                "state": "detected",
                "value": 1,
                "simulated": True,
                "timestamp": ts
            }

            topic = f"smarthome/{device_id}/sensors/{component.lower()}"
            mqtt_publisher.publish(topic, payload, use_batch=True)

        time.sleep(duration)

        if stop_event.is_set():
            break

        ts = time.time()
        print_fn(f"{component} Motion stopped")

        if mqtt_publisher and mqtt_publisher.connected:
            payload = {
                "device_id": device_id,
                "sensor_type": "door_motion_sensor",
                "component": component,
                "state": "stopped",
                "value": 0,
                "simulated": True,
                "timestamp": ts
            }

            topic = f"smarthome/{device_id}/sensors/{component.lower()}"
            mqtt_publisher.publish(topic, payload, use_batch=True)

        time.sleep(duration)

    print_fn(f"{component} simulator stopped")
