import time
import random

def run_dl_simulator(stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):

    print_fn("DL simulator started")

    current_state = False

    while not stop_event.is_set():
        time.sleep(random.randrange(10, 30))

        if stop_event.is_set():
            break

        current_state = not current_state
        timestamp = time.time()

        state_str = "ON" if current_state else "OFF"
        print_fn(f"{time.ctime()} Door light turned {state_str} (simulated)")

        if mqtt_publisher and mqtt_publisher.connected:
            data = {
                "device_id": device_id,
                "sensor_type": "door_light",
                "component": "DL",
                "state": current_state,
                "simulated": True,
                "timestamp": timestamp
            }

            topic = f"smarthome/{device_id}/sensors/dl"
            mqtt_publisher.publish(topic, data, use_batch=True)

    print_fn("DL simulator stopped")
