import time
import random

def run_ds1_simulator(stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):

    print_fn("Door sensor simulator started")
    
    while not stop_event.is_set():
        state = random.choice(["OPEN", "CLOSED"])
        timestamp = time.time()
        
        print_fn(f"{time.ctime()} Door state: {state}")
        
        if mqtt_publisher and mqtt_publisher.connected:
            data = {
                "device_id": device_id,
                "sensor_type": "door_sensor",
                "component": "DS1",
                "state": state.lower(),
                "value": 1 if state == "OPEN" else 0,
                "simulated": True,
                "timestamp": timestamp
            }
            
            topic = f"smarthome/{device_id}/sensors/ds1"
            mqtt_publisher.publish(topic, data, use_batch=True)
        
        time.sleep(2)
    
    print_fn("Door sensor simulator stopped")