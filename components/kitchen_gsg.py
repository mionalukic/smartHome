import threading
from simulators.kitchen_gsg import run_kitchen_gsg_simulator


def run_kitchen_gsg(settings, threads, stop_event,
                    print_fn=print, mqtt_publisher=None):

    device_id = settings.get("device_id", "pi")
    component = settings.get("component", "GSG")
    interval = settings.get("interval", 0.5)
    threshold = settings.get("threshold", 20000)

    if settings.get("simulated", True):
        t = threading.Thread(
            target=run_kitchen_gsg_simulator,
            args=(stop_event, print_fn, mqtt_publisher, device_id, component, interval)
        )
    else:
        from sensors.kitchen_gsg import run_kitchen_gsg
        t = threading.Thread(
            target=run_kitchen_gsg,
            args=(stop_event, print_fn, mqtt_publisher,
                  device_id, component, interval, threshold)
        )

    t.start()
    threads.append(t)
