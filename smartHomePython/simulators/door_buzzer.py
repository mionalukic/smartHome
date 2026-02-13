import time
import random

def run_db_simulator(stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):

    print_fn("DB simulator started")
    
    while not stop_event.is_set():
        time.sleep(random.randrange(5, 15))
        
        if stop_event.is_set():
            break
        
        pitch = random.choice([440, 880, 660])  # A4, A5, E5
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