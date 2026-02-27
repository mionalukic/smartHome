from inspect import stack
import threading
from simulators.door_ultrasonic_sensor import run_ultrasonic_simulator

DUS1_STACK = []
DUS2_STACK = []
def is_entering(device_id):
    if device_id.startswith("pi1"):
        if len(DUS1_STACK) < 2:
            return None
        return True if DUS1_STACK[-1] - DUS1_STACK[-2] >= 0 else False
    else:
        if len(DUS2_STACK) < 2:
            return None
        return True if DUS2_STACK[-1] - DUS2_STACK[-2] >= 0 else False
    
def add_measurement(device_id, value):
    if device_id.startswith("pi1"):
        DUS1_STACK.append(value)
    elif device_id.startswith("pi2"):
        DUS2_STACK.append(value)

def run_dus(settings, threads, stop_event, print_fn=print, mqtt_publisher=None, device_id="unknown"):
    device_id = device_id if device_id else settings.get("device_id", "pi")
    component = settings.get("component", "DUS")

    if settings.get("simulated", True):
        t = threading.Thread(
            target=run_ultrasonic_simulator,
            args=(stop_event, print_fn, mqtt_publisher, device_id, component, add_measurement)
        )
    else:
        from sensors.door_ultrasonic_sensor import run_ultrasonic
        t = threading.Thread(
            target=run_ultrasonic,
            args=(
                settings["trig"],
                settings["echo"],
                stop_event,
                print_fn,
                mqtt_publisher,
                device_id,
                component,
                add_measurement
            )
        )

    t.start()
    threads.append(t)
