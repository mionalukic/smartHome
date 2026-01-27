import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

def run_dus1_ultrasonic(trig_pin, echo_pin, stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):

    if GPIO is None:
        print_fn("GPIO not available, cannot run real ultrasonic sensor")
        return
    
    GPIO.setup(trig_pin, GPIO.OUT)
    GPIO.setup(echo_pin, GPIO.IN)
    
    print_fn("Ultrasonic sensor (REAL) started")
    
    def get_distance():
        GPIO.output(trig_pin, False)
        time.sleep(0.2)
        
        GPIO.output(trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(trig_pin, False)
        
        pulse_start = time.time()
        pulse_end = time.time()
        
        timeout = time.time() + 0.04
        while GPIO.input(echo_pin) == 0:
            if time.time() > timeout:
                return None
            pulse_start = time.time()
        
        timeout = time.time() + 0.04
        while GPIO.input(echo_pin) == 1:
            if time.time() > timeout:
                return None
            pulse_end = time.time()
        
        pulse_duration = pulse_end - pulse_start
        return round((pulse_duration * 34300) / 2, 2)
    
    while not stop_event.is_set():
        distance = get_distance()
        timestamp = time.time()
        
        if distance is not None:
            print_fn(f"Distance: {distance} cm")
            
            if mqtt_publisher and mqtt_publisher.connected:
                data = {
                    "device_id": device_id,
                    "sensor_type": "ultrasonic_sensor",
                    "component": "DUS1",
                    "trig_pin": trig_pin,
                    "echo_pin": echo_pin,
                    "distance_cm": distance,
                    "unit": "cm",
                    "timestamp": timestamp
                }
                
                topic = f"smarthome/{device_id}/sensors/dus1"
                mqtt_publisher.publish(topic, data, use_batch=True)
        else:
            print_fn("Measurement timeout")
            
            if mqtt_publisher and mqtt_publisher.connected:
                data = {
                    "device_id": device_id,
                    "sensor_type": "ultrasonic_sensor",
                    "component": "DUS1",
                    "trig_pin": trig_pin,
                    "echo_pin": echo_pin,
                    "error": "measurement_timeout",
                    "timestamp": timestamp
                }
                
                topic = f"smarthome/{device_id}/sensors/dus1"
                mqtt_publisher.publish(topic, data, use_batch=True)
        
        time.sleep(1)
    
    GPIO.cleanup([trig_pin, echo_pin])
    print_fn("Ultrasonic sensor stopped")