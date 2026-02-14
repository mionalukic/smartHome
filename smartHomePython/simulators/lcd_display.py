import time
import random


def run_lcd_simulator(settings, stop_event, print_fn=print,
                      mqtt_publisher=None, device_id='pi1'):

    cols = settings.get("cols", 16)
    rows = settings.get("rows", 2)
    refresh = settings.get("refresh_interval", 5)

    print_fn(f"LCD simulator started ({cols}x{rows})")

    messages = [
        ("Smart Home", "System Ready"),
        ("Door Status", "Closed"),
        ("Door Status", "Opened"),
        ("Temperature", "22.5 C"),
        ("Alarm", "Inactive"),
        ("Welcome", "Have a nice day")
    ]

    while not stop_event.is_set():
        time.sleep(refresh)

        if stop_event.is_set():
            break

        line1, line2 = random.choice(messages)

        # Trim to LCD size
        line1 = line1[:cols]
        line2 = line2[:cols]

        print_fn(f"[SIM LCD]\n{line1}\n{line2}")

        if mqtt_publisher and mqtt_publisher.connected:
            data = {
                "device_id": device_id,
                "sensor_type": "lcd_display",
                "component": "LCD",
                "line1": line1,
                "line2": line2,
                "simulated": True,
                "timestamp": time.time()
            }

            topic = f"smarthome/{device_id}/sensors/lcd"
            mqtt_publisher.publish(topic, data, use_batch=True)

    print_fn("LCD simulator stopped")
