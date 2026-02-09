import threading
from simulators.door_ultrasonic_sensor import run_ultrasonic_simulator


def run_dus(settings, threads, stop_event, print_fn=print, mqtt_publisher=None):
    device_id = settings.get("device_id", "pi")
    component = settings.get("component", "DUS")

    if settings.get("simulated", True):
        t = threading.Thread(
            target=run_ultrasonic_simulator,
            args=(stop_event, print_fn, mqtt_publisher, device_id, component)
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
                component
            )
        )

    t.start()
    threads.append(t)
