import threading
from simulators.door_motion_sensor import run_dpir_simulator


def run_dpir(settings, threads, stop_event,
             print_fn=print, mqtt_publisher=None, device_id="unknown"):

    device_id = device_id if device_id else settings.get("device_id", "pi")
    component = settings.get("component", "DPIR")

    if settings.get("simulated", True):
        t = threading.Thread(
            target=run_dpir_simulator,
            args=(stop_event, print_fn, mqtt_publisher, device_id, component)
        )
    else:
        from sensors.door_motion_sensor import DPIR, run_dpir_loop
        dpir = DPIR(settings["pin"], component)
        t = threading.Thread(
            target=run_dpir_loop,
            args=(dpir, stop_event, print_fn, mqtt_publisher, device_id)
        )

    t.start()
    threads.append(t)
