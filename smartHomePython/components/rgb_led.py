import json
import threading
from simulators.door_motion_sensor import run_dpir_simulator

commmand = "off"

def on_command_message(client, userdata, msg):
    print(f"[MQTT] Received message on topic {msg.topic}")
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        # print(f"[MQTT] Received DHT message: {payload}")
        component = payload.get("component", "UNKNOWN")
        commmand = payload.get("command", "off")
        print(f"[RGB_LED] Received data for {component}: Command={commmand}")
    except json.JSONDecodeError as e:
        print(f"[RGB_LED] Error decoding MQTT message: {e}")
    except Exception as e:
        print(f"[RGB_LED] Error processing RGB LED message: {e}")

def run_rgb(settings, threads, stop_event,
             print_fn=print, mqtt_publisher=None, device_id="unknown"):

    device_id = device_id if device_id else settings.get("device_id", "pi3_bedroom_001")
    component = settings.get("component", "RGB_LED")

    if settings.get("simulated", True):
        t = threading.Thread(
            target=run_dpir_simulator,
            args=(stop_event, print_fn, mqtt_publisher, device_id, component)
        )
    else:
        from sensors.rgb_led import RGBLED, run_rgb_led_loop
        rgb = RGBLED(settings.get("red_pin", 12), settings.get("green_pin", 13), settings.get("blue_pin", 19))
        t = threading.Thread(
            target=run_rgb_led_loop,
            args=(rgb, stop_event, commmand, print_fn, mqtt_publisher, device_id)
        )

    t.start()
    threads.append(t)
