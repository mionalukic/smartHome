import time
import random


def run_lcd_simulator(stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):
    print_fn("LCD simulator started")

    messages = [
        ("Smart Home", "System Ready"),
        ("Door Status", "Closed"),
        ("Door Status", "Opened"),
        ("Temperature", "22.5 C"),
        ("Alarm", "Inactive"),
        ("Welcome", "Have a nice day")
    ]

    while not stop_event.is_set():
        time.sleep(random.randrange(5, 12))

        if stop_event.is_set():
            break

        line1, line2 = random.choice(messages)
        timestamp = time.time()

        print_fn(f"{time.ctime()} LCD display:\n{line1}\n{line2}")

        if mqtt_publisher and mqtt_publisher.connected:
            data = {
                "device_id": device_id,
                "sensor_type": "lcd_display",
                "component": "LCD",
                "line1": line1,
                "line2": line2,
                "simulated": True,
                "timestamp": timestamp
            }

            topic = f"smarthome/{device_id}/sensors/lcd"
            mqtt_publisher.publish(topic, data, use_batch=True)

    print_fn("LCD simulator stopped")
