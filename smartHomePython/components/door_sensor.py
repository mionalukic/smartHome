import threading
from simulators.door_sensor import run_door_simulator


def run_ds(settings, component, threads, stop_event,
                    print_fn=print, mqtt_publisher=None, device_id="unknown"):

    if settings.get("simulated", True):
        from simulators.door_sensor import run_door_simulator

        t = threading.Thread(
            target=run_door_simulator,
            args=(stop_event, print_fn, mqtt_publisher, device_id, component)
        )

    else:
        from sensors.door_sensor import run_real_door_sensor

        t = threading.Thread(
            target=run_real_door_sensor,
            args=(settings["pin"], stop_event, print_fn,
                  mqtt_publisher, device_id, component)
        )

    t.start()
    threads.append(t)

def publish_door_event(mqtt_publisher, device_id,
                       component, state, simulated=True):

    import time

    payload = {
        "device_id": device_id,
        "sensor_type": "door_sensor",
        "component": component,
        "state": state,
        "value": 1 if state == "open" else 0,
        "simulated": simulated,
        "timestamp": time.time()
    }

    topic = f"smarthome/{device_id}/sensors/{component.lower()}"

    if mqtt_publisher and mqtt_publisher.connected:
        mqtt_publisher.publish(topic, payload, use_batch=True)
