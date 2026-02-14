import time
try:
    import RPi.GPIO as GPIO
    import LA_DHT as DHT
except ImportError:
    GPIO = None
    DHT = None


def run_kitchen_dht(pin, stop_event, print_fn=print,
                    mqtt_publisher=None,
                    device_id="pi",
                    component="DHT3",
                    interval=2):

    if GPIO is None or DHT is None:
        print_fn("DHT GPIO library not available")
        return

    dht = DHT.DHT(pin)
    print_fn("Kitchen DHT (REAL) started")

    while not stop_event.is_set():
        chk = dht.readDHT11()
        ts = time.time()

        if chk == dht.DHTLIB_OK:
            temp = dht.temperature
            hum = dht.humidity

            print_fn(f"DHT TEMP={temp:.1f}°C HUM={hum:.1f}%")

            if mqtt_publisher and mqtt_publisher.connected:
                payload = {
                    "device_id": device_id,
                    "sensor_type": "kitchen_dht",
                    "component": component,
                    "temperature": temp,
                    "humidity": hum,
                    "timestamp": ts
                }

                topic = f"smarthome/{device_id}/sensors/{component.lower()}"
                mqtt_publisher.publish(topic, payload, use_batch=True)
        else:
            print_fn("DHT read error")

        time.sleep(interval)

    GPIO.cleanup(pin)
    print_fn("Kitchen DHT stopped")
