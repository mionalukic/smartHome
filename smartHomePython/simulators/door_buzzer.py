import time
import random

def run_db_simulator(stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1', get_DB_state=None):

    print_fn("DB simulator started")
    
    while not stop_event.is_set():
        time.sleep(1)
        state = get_DB_state()
        if state is None or not state:
            continue
        
        pitch = random.choice([440, 880, 660])
        duration = random.uniform(0.1, 0.5)
        timestamp = time.time()
        
        print_fn(f"{time.ctime()} Buzzer activated: pitch={pitch}Hz, duration={duration:.2f}s")
        
        if mqtt_publisher and mqtt_publisher.connected:
            data = {
                "device_id": device_id,
                "sensor_type": "door_buzzer",
                "component": "DB",
                "pitch": pitch,
                "duration": duration,
                "simulated": True,
                "timestamp": timestamp
            }
            
            topic = f"smarthome/{device_id}/sensors/db"
            mqtt_publisher.publish(topic, data, use_batch=True)
    
    print_fn("DB simulator stopped")