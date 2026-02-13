import threading
from simulators.door_sensor1 import run_ds1_simulator


def run_ds1(settings, threads, stop_event, print_fn=print, mqtt_publisher=None, device_id="unknown"):
    
    if settings["simulated"]:
        t = threading.Thread(
            target=run_ds1_simulator,
            args=(stop_event, print_fn, mqtt_publisher, device_id)
        )
    else:
        from sensors.door_sensor1 import run_ds1_button
        t = threading.Thread(
            target=run_ds1_button,
            args=(settings["pin"], stop_event, print_fn, mqtt_publisher, device_id)
        )

    t.start()
    threads.append(t)