import threading
from simulators.door_sensor2 import run_ds2_simulator


def run_ds2(settings, threads, stop_event, print_fn=print, mqtt_publisher=None):
    device_id = settings.get("device_id", "pi2")

    if settings.get("simulated", True):
        t = threading.Thread(
            target=run_ds2_simulator,
            args=(stop_event, print_fn, mqtt_publisher, device_id)
        )
    else:
        from sensors.door_sensor2 import run_ds2_button
        t = threading.Thread(
            target=run_ds2_button,
            args=(settings["pin"], stop_event, print_fn, mqtt_publisher, device_id)
        )

    t.start()
    threads.append(t)
