import RPi.GPIO as GPIO
import time

class DB(object):
    def __init__(self, pin):
        self.pin = pin
        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = 'pi1'
        
    def setup(self, print_fn=print, mqtt_publisher=None, device_id='pi1'):
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        
        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id
        
    def buzz(self, pitch, duration):
        period = 1.0 / pitch
        delay = period / 2
        cycles = int(duration * pitch)
        
        self.print_fn(f"Buzzing: pitch={pitch}Hz, duration={duration:.2f}s")
        
        if self.mqtt_publisher and self.mqtt_publisher.connected:
            data = {
                "device_id": self.device_id,
                "sensor_type": "door_buzzer",
                "component": "DB",
                "pitch": pitch,
                "duration": duration,
                "timestamp": time.time()
            }
            
            topic = f"smarthome/{self.device_id}/sensors/db"
            self.mqtt_publisher.publish(topic, data, use_batch=True)
        
        for _ in range(cycles):
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(delay)

def run_db_loop(db, stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):
   
    db.setup(print_fn, mqtt_publisher, device_id)
    
    print_fn("DB ready for buzzing")
    
    while not stop_event.is_set():
        time.sleep(10)
        if stop_event.is_set():
            break
        db.buzz(440, 0.2)  
    
    print_fn("DB loop stopped")
