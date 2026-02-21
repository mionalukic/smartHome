import json
import threading
from simulators.rgb_led import run_rgb_led_simulator

BUTTON_COLOR_MAP = {
    "1": "red",
    "2": "green",
    "3": "blue",
    "4": "white",
    "5": "yellow",
    "6": "purple",
    "7": "light_blue",
    "0": "off"
}
from queue import Queue, Empty

color_queue = Queue()

def on_command_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        button = payload.get("button")
        if button in BUTTON_COLOR_MAP:
            color_queue.put(BUTTON_COLOR_MAP[button])
    except Exception as e:
        print(f"[RGB] Error handling IR message: {e}")


def run_rgb(settings, threads, stop_event,
             print_fn=print, mqtt_publisher=None, device_id="unknown"):

    device_id = device_id if device_id else settings.get("device_id", "pi3_bedroom_001")
    component = settings.get("component", "RGB_LED")

    if settings.get("simulated", True):
        print_fn(f"Starting RGB LED simulator for {device_id}")
    else:
        print_fn(f"Starting real RGB LED for {device_id}")

    if settings.get("simulated", True):
        t = threading.Thread(
            target=run_rgb_led_simulator,
            args=(color_queue, print_fn, mqtt_publisher, device_id)
        )
    else:
        from sensors.rgb_led import RGBLED, run_rgb_led_loop
        rgb = RGBLED(settings.get("red_pin", 12), settings.get("green_pin", 13), settings.get("blue_pin", 19))
        t = threading.Thread(
            target=run_rgb_led_loop,
            args=(rgb, stop_event, color_queue, print_fn, mqtt_publisher, device_id)
        )

    t.start()
    threads.append(t)
