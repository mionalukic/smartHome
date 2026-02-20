import time
import random


def run_kitchen_button_simulator(stop_event, print_fn=print,
                                 mqtt_publisher=None,
                                 device_id="pi",
                                 component="BTN"):

    print_fn("Kitchen BTN simulator started")

    while not stop_event.is_set():
        time.sleep(random.randint(4, 8))

        print_fn("BTN Kitchen button: pressed")

        if mqtt_publisher and mqtt_publisher.connected:
            payload = {
                "device_id": device_id,
                "sensor_type": "kitchen_button",
                "component": component,
                "event": "pressed",
                "value": 1,
                "simulated": True,
                "timestamp": time.time()
            }

            topic = f"smarthome/{device_id}/sensors/{component.lower()}"
            mqtt_publisher.publish(topic, payload, use_batch=True)

    print_fn("Kitchen BTN simulator stopped")


def publish_kitchen_button_press(mqtt_publisher, device_id,
                                 component="BTN", simulated=True):

    if not mqtt_publisher or not mqtt_publisher.connected:
        return

    payload = {
        "device_id": device_id,
        "sensor_type": "kitchen_button",
        "component": component,
        "event": "pressed",
        "value": 1,
        "simulated": simulated,
        "timestamp": time.time()
    }

    topic = f"smarthome/{device_id}/sensors/{component.lower()}"
    mqtt_publisher.publish(topic, payload, use_batch=True)