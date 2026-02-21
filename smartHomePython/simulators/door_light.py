import time
import random

def run_dl_simulator(stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1', get_dl_state=None, turn_off=None, do_change=None):
    print_fn("DL simulator started")

    current_state = None
    start_time = None
    while not stop_event.is_set():
        state, should_change = get_dl_state() if get_dl_state else None
        if state is None or state == current_state:
            if current_state and should_change:
                start_time = time.time()
                if do_change != None : do_change()
            if start_time != None and turn_off != None and current_state == True and time.time() - start_time > 10:
                turn_off()
            time.sleep(0.1)
            continue
        current_state = state
        if do_change != None : do_change()
        start_time = time.time()

        state_str = "ON" if current_state else "OFF"
        print_fn(f"Door light turned {state_str}")

        if mqtt_publisher and mqtt_publisher.connected:
            data = {
                "device_id": device_id,
                "sensor_type": "door_light",
                "component": "DL",
                "value": 1 if current_state else 0,
                "simulated": True,
                "timestamp": time.time()
            }

            topic = f"smarthome/{device_id}/sensors/dl"
            mqtt_publisher.publish(topic, data, use_batch=True)
        time.sleep(0.1)

    print_fn("DL simulator stopped")
