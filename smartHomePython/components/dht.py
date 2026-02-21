import threading
from simulators.dht import run_dht_simulator


def run_dht(settings, threads, stop_event,
                    print_fn=print, mqtt_publisher=None,device_id="unknown"):

    device_id = device_id if device_id else settings.get("device_id", "pi")
    component = settings.get("component", "DHT3")
    interval = settings.get("interval", 2)

    if settings.get("simulated", True):
        t = threading.Thread(
            target=run_dht_simulator,
            args=(stop_event, print_fn, mqtt_publisher, device_id, component, interval)
        )
    else:
        from sensors.dht import run_dht
        t = threading.Thread(
            target=run_dht,
            args=(
                settings["pin"],
                stop_event,
                print_fn,
                mqtt_publisher,
                device_id,
                component,
                interval
            )
        )

    t.start()
    threads.append(t)
