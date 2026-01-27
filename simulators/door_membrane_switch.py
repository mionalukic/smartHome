import time
import random

def run_dms_simulator(stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):
    """
    Simulate door membrane switch (keypad) key presses
    
    Args:
        stop_event: Threading event for stopping
        print_fn: Function for logging
        mqtt_publisher: Optional MQTT publisher
        device_id: Device identifier
    """
    keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]
    
    print_fn("DMS simulator started")
    
    while not stop_event.is_set():
        # Random delay between key presses
        time.sleep(random.randrange(3, 8))
        
        if stop_event.is_set():
            break
        
        key = random.choice(keys)
        timestamp = time.time()
        
        print_fn(f"{time.ctime()} Key pressed: {key}")
        
        # Publish to MQTT if available
        if mqtt_publisher and mqtt_publisher.connected:
            # Simulate press event
            data_press = {
                "device_id": device_id,
                "sensor_type": "door_membrane_switch",
                "component": "DMS",
                "key": key,
                "event": "press",
                "simulated": True,
                "timestamp": timestamp
            }
            
            topic = f"smarthome/{device_id}/sensors/dms"
            mqtt_publisher.publish(topic, data_press, use_batch=True)
            
            # Simulate release event after short delay
            time.sleep(0.1)
            
            data_release = {
                "device_id": device_id,
                "sensor_type": "door_membrane_switch",
                "component": "DMS",
                "key": key,
                "event": "release",
                "simulated": True,
                "timestamp": time.time()
            }
            
            mqtt_publisher.publish(topic, data_release, use_batch=True)
    
    print_fn("DMS simulator stopped")