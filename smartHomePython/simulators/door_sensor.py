import time
import random

def run_door_simulator(stop_event, print_fn,
                       mqtt_publisher, device_id, component):

    import random, time

    print_fn(f"{component} simulator started")

    while not stop_event.is_set():

        state = random.choice(["open", "closed"])
        print_fn(f"{component} state: {state.upper()}")

        payload = {
            "device_id": device_id,
            "sensor_type": "door_sensor",
            "component": component,
            "state": state,
            "value": 1 if state == "open" else 0,
            "simulated": True,
            "timestamp": time.time()
        }

        topic = f"smarthome/{device_id}/sensors/{component.lower()}"
        mqtt_publisher.publish(topic, payload, use_batch=True)

        time.sleep(2)

