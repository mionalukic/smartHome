import time

def run_lcd_simulator(settings, stop_event, print_fn=print,
                      mqtt_publisher=None, device_id='pi1', dht_data=None):

    cols = settings.get("cols", 16)
    refresh = settings.get("refresh_interval", 5)

    print_fn(f"LCD simulator started ({cols}x{settings.get('rows', 2)})")

    sensor_keys = ["DHT1", "DHT2", "DHT3"]
    index = 0

    while not stop_event.is_set():

        sensor_name = sensor_keys[index]

        temp, hum = dht_data.get(sensor_name, ("--", "--"))

        line1 = f"{sensor_name} Temp:"
        line2 = f"{temp}C Hum:{hum}%"
        

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

        index = (index + 1) % len(sensor_keys)
        time.sleep(refresh)

    print_fn("LCD simulator stopped")
