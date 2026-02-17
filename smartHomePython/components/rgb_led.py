import json
import threading
from simulators.rgb_led import run_rgb_led_simulator

color_state = {"value": "white"}

def on_command_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        color_state["value"] = payload.get("command", "white")
        print(f"[RGB_LED] New command: {color_state['value']}")
    except Exception as e:
        print(f"[RGB_LED] Error: {e}")


def run_rgb(settings, threads, stop_event,
             print_fn=print, mqtt_publisher=None, device_id="unknown"):

    device_id = device_id if device_id else settings.get("device_id", "pi3_bedroom_001")
    component = settings.get("component", "RGB_LED")

    if settings.get("simulated", True):
        t = threading.Thread(
            target=run_rgb_led_simulator,
            args=(color_state, print_fn, mqtt_publisher, device_id)
        )
    else:
        from sensors.rgb_led import RGBLED, run_rgb_led_loop
        rgb = RGBLED(settings.get("red_pin", 12), settings.get("green_pin", 13), settings.get("blue_pin", 19))
        t = threading.Thread(
            target=run_rgb_led_loop,
            args=(rgb, stop_event, color_state, print_fn, mqtt_publisher, device_id)
        )

    t.start()
    threads.append(t)
