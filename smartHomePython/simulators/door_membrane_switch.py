import time
import random

def run_dms_simulator(stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):

    keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]
    
    print_fn("DMS simulator started")
    
    while not stop_event.is_set():
        time.sleep(random.randrange(3, 8))
        
        if stop_event.is_set():
            break
        
        key = random.choice(keys)
        timestamp = time.time()
        
        print_fn(f"{time.ctime()} Key pressed: {key}")
        
        if mqtt_publisher and mqtt_publisher.connected:
            data = {
                "device_id": device_id,
                "sensor_type": "door_membrane_switch",
                "component": "DMS",
                "key": key,
                "simulated": True,
                "timestamp": timestamp
            }
            
            topic = f"smarthome/{device_id}/sensors/dms"
            mqtt_publisher.publish(topic, data, use_batch=True)
            
    print_fn("DMS simulator stopped")