import time
import threading
import json
from simulators.lcd_display import run_lcd_simulator

dht_data = {}

def on_dht_message(client, userdata, msg):
    # print(f"[MQTT] Received message on topic {msg.topic}")
    try:

        payload = json.loads(msg.payload.decode('utf-8'))
        component = payload.get("component", "UNKNOWN")
        temp = payload.get("temperature", "--")
        hum = payload.get("humidity", "--")
        dht_data[component] = (temp, hum)
        # print(f"[DHT] Received data for {component}: Temp={temp}°C Hum={hum}%")
    except json.JSONDecodeError as e:
        print(f"[LCD] Error decoding MQTT message: {e}")
    except Exception as e:
        print(f"[LCD] Error processing DHT message: {e}")


def run_lcd(settings, threads, stop_event,
            print_fn=print, mqtt_publisher=None, state=None, device_id="pi3_bedroom_001"):

    simulated = settings.get("simulated", True)
    refresh = settings.get("refresh_interval", 5)
    sensor_keys = ["DHT1", "DHT2", "DHT3"]
    
    print_fn(f"LCD state: {state} | simulated={simulated}")
    
    if simulated:
        if state:
            lcd_thread = threading.Thread(
                target=run_lcd_simulator,
                args=(settings, stop_event, print_fn, mqtt_publisher, device_id, dht_data, sensor_keys),
                daemon=True
            )
            lcd_thread.start()
            threads.append(lcd_thread)
            
        state_str = "on" if state else "off"
        print_fn(f"LCD turned {state_str} (simulated)")
    else:
        if state:
            from sensors.lcd.lcd_display import run_lcd_loop, LCD
            
            lcd = LCD(settings)
            lcd.setup(print_fn, mqtt_publisher, device_id)
            
            lcd_thread = threading.Thread(
                target=run_lcd_loop, 
                args=(lcd, sensor_keys, stop_event, print_fn, dht_data, refresh),
                daemon=True
            )
            lcd_thread.start()
            threads.append(lcd_thread)
            print_fn("Real LCD started")
        else:
            print_fn("LCD turned off")