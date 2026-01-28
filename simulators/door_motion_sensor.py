import time
import random

def run_dpir_simulator(stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):

    print_fn("DPIR simulator started")
    
    while not stop_event.is_set():
        duration = random.randrange(3, 5)
        
        timestamp_detected = time.time()
        print_fn(f"{time.ctime()} Detected movement")
        
        if mqtt_publisher and mqtt_publisher.connected:
            data_detected = {
                "device_id": device_id,
                "sensor_type": "door_motion_sensor",
                "component": "DPIR1",
                "state": "detected",
                "value": 1,
                "simulated": True,
                "timestamp": timestamp_detected
            }
            
            topic = f"smarthome/{device_id}/sensors/dpir1"
            mqtt_publisher.publish(topic, data_detected, use_batch=True)
        
        time.sleep(duration)
        
        if stop_event.is_set():
            break
        
        timestamp_stopped = time.time()
        print_fn(f"{time.ctime()} Stopped detecting movement")
        
        if mqtt_publisher and mqtt_publisher.connected:
            data_stopped = {
                "device_id": device_id,
                "sensor_type": "door_motion_sensor",
                "component": "DPIR1",
                "state": "stopped",
                "value": 0,
                "simulated": True,
                "timestamp": timestamp_stopped
            }
            
            topic = f"smarthome/{device_id}/sensors/dpir1"
            mqtt_publisher.publish(topic, data_stopped, use_batch=True)
        
        time.sleep(duration)
    
    print_fn("DPIR simulator stopped")