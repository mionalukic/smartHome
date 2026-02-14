import time
import threading
from simulators.lcd_display import run_lcd_simulator


def run_lcd(settings, threads, stop_event,
            print_fn=print, mqtt_publisher=None, state=None):

    device_id = settings.get("device_id", "pi1")
    simulated = settings.get("simulated", True)

    print_fn(f"LCD state: {state} | simulated={simulated}")


    if simulated:

        if state is not None:
            state_str = "on" if state else "off"
            print_fn(f"LCD turned {state_str} (simulated)")

            if mqtt_publisher and mqtt_publisher.connected:
                data = {
                    "device_id": device_id,
                    "device": "lcd_display",
                    "component": "LCD",
                    "value": 1 if state else 0,
                    "simulated": True,
                    "timestamp": time.time()
                }

                topic = f"smarthome/{device_id}/actuators/lcd"
                mqtt_publisher.publish(topic, data, use_batch=True)

        else:
            lcd_thread = threading.Thread(
                target=run_lcd_simulator,
                args=(settings, stop_event, print_fn,
                      mqtt_publisher, device_id)
            )
            lcd_thread.start()
            threads.append(lcd_thread)

    else:
        if state:
            from sensors.lcd.lcd_display import run_lcd_loop, LCD

            lcd = LCD(settings)

            lcd_thread = threading.Thread(
                target=run_lcd_loop,
                args=(lcd, settings, stop_event,
                      print_fn, mqtt_publisher, device_id)
            )
            lcd_thread.start()
            threads.append(lcd_thread)

            print_fn("Real LCD started")

        else:
            print_fn("LCD turned off")
