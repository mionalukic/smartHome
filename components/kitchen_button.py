import threading
from simulators.kitchen_button import run_kitchen_button_simulator


def run_kitchen_button(settings, threads, stop_event,
                       print_fn=print, mqtt_publisher=None):
    

    device_id = settings.get("device_id", "pi")
    component = settings.get("component", "BTN")

    if settings.get("simulated", True):
        t = threading.Thread(
            target=run_kitchen_button_simulator,
            args=(stop_event, print_fn, mqtt_publisher, device_id, component)
        )
    else:
        from sensors.kitchen_button import KitchenButton, run_kitchen_button_loop
        button = KitchenButton(settings["pin"], component)
        t = threading.Thread(
            target=run_kitchen_button_loop,
            args=(button, stop_event, print_fn, mqtt_publisher, device_id)
        )

    t.start()
    threads.append(t)
