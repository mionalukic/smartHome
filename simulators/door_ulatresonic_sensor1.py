import time
import random

def generate_values(initial_distance=120):
    distance = initial_distance
    MIN_DISTANCE = 10
    MAX_DISTANCE = 200
    while True:
        distance += random.randint(-3, 3)
        distance = max(MIN_DISTANCE, min(MAX_DISTANCE, distance))
        yield distance

def run_dus1_simulator(stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):

    generator = generate_values()
    print_fn("Ultrasonic simulator started")
    
    while not stop_event.is_set():
        distance = next(generator)
        timestamp = time.time()
        
        print_fn(f"{time.ctime()} Distance: {distance} cm")
        
        if mqtt_publisher and mqtt_publisher.connected:
            data = {
                "device_id": device_id,
                "sensor_type": "ultrasonic_sensor",
                "component": "DUS1",
                "distance_cm": distance,
                "unit": "cm",
                "simulated": True,
                "timestamp": timestamp
            }
            
            topic = f"smarthome/{device_id}/sensors/dus1"
            mqtt_publisher.publish(topic, data, use_batch=True)
        
        time.sleep(1)
    
    print_fn("Ultrasonic simulator stopped")