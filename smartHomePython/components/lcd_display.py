import time
import threading
from simulators.lcd_display import run_lcd_simulator

dht_data = {}

def on_dht_message(payload):
    component = payload.get("component")
    temp = payload.get("temperature", "--")
    hum = payload.get("humidity", "--")
    dht_data[component] = (temp, hum)
    print(f"Received DHT data: {component} temp={temp}C hum={hum}%")


def run_lcd(settings, threads, stop_event,
            print_fn=print, mqtt_publisher=None, state=None):

    device_id = settings.get("device_id", "pi1")
    simulated = settings.get("simulated", True)
    refresh = settings.get("refresh_interval", 5)
    sensor_keys = ["DHT1", "DHT2", "DHT3"]

    print_fn(f"LCD state: {state} | simulated={simulated}")

    if simulated:
        if state:
            lcd_thread = threading.Thread(
                target=run_lcd_simulator,
                args=(settings, stop_event, print_fn, mqtt_publisher, device_id, dht_data)
            )
            lcd_thread.start()
            threads.append(lcd_thread)

        state_str = "on" if state else "off"
        print_fn(f"LCD turned {state_str} (simulated)")

        if mqtt_publisher and mqtt_publisher.connected:
            data = {
                "device_id": device_id,
                "device": "lcd_display",
                "component": "LCD",
                "value": state_str,
                "simulated": True,
                "timestamp": time.time()
            }
            topic = f"smarthome/{device_id}/actuators/lcd"
            mqtt_publisher.publish(topic, data, use_batch=True)

    else:
        if state:
            from sensors.lcd.lcd_display import run_lcd_loop, LCD

            lcd = LCD(settings)
            lcd.setup(print_fn, mqtt_publisher, device_id)
            
            lcd_thread = threading.Thread(target=run_lcd_loop, args=(lcd, sensor_keys, stop_event, print_fn, dht_data, refresh))
            lcd_thread.start()
            threads.append(lcd_thread)

            print_fn("Real LCD started")
        else:
            print_fn("LCD turned off")
