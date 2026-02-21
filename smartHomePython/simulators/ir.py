import random
from time import sleep, time

BUTTONS = ["0", "1", "2", "3", "4", "5", "6", "7"]

def run_ir_sensor_simulator(stop_event, print_fn=print, mqtt_publisher=None, device_id="pi3"):
    while not stop_event.is_set():
        # brža reakcija za test
        sleep(random.uniform(3.0, 4.0))

        button = random.choice(BUTTONS)
        print_fn(f"Simulated button: {button}")

        if mqtt_publisher and getattr(mqtt_publisher, "connected", False):
            payload = {
                "device_id": device_id,
                "sensor_type": "ir",
                "component": "IR",
                "value": int(button),
                "hex_code": "0xSIMULATED",
                "simulated": True,
                "timestamp": time()
            }

            topic = f"smarthome/{device_id}/sensors/ir"
            mqtt_publisher.publish(topic, payload, use_batch=True)
    print_fn(f"IR sensor simulator stopped for device {device_id}")
    
