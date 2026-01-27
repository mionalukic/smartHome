import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

class DS1(object):
    def __init__(self, pin):
        self.pin = pin
        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = 'pi1'
        
    def setup(self, print_fn=print, mqtt_publisher=None, device_id='pi1'):
        if GPIO is None:
            print_fn("GPIO not available, cannot setup door sensor")
            return
            
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id
        
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.door_opened, bouncetime=200)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.door_closed, bouncetime=200)
    
    def door_opened(self, channel):
        self.print_fn("Door state: OPEN")
        
        if self.mqtt_publisher and self.mqtt_publisher.connected:
            data = {
                "device_id": self.device_id,
                "sensor_type": "door_sensor",
                "component": "DS1",
                "pin": self.pin,
                "state": "open",
                "value": 1,
                "timestamp": time.time()
            }
            
            topic = f"smarthome/{self.device_id}/sensors/ds1"
            self.mqtt_publisher.publish(topic, data, use_batch=True)
    
    def door_closed(self, channel):
        self.print_fn("Door state: CLOSED")
        
        if self.mqtt_publisher and self.mqtt_publisher.connected:
            data = {
                "device_id": self.device_id,
                "sensor_type": "door_sensor",
                "component": "DS1",
                "pin": self.pin,
                "state": "closed",
                "value": 0,
                "timestamp": time.time()
            }
            
            topic = f"smarthome/{self.device_id}/sensors/ds1"
            self.mqtt_publisher.publish(topic, data, use_batch=True)

def run_ds1_button(pin, stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):
 
    if GPIO is None:
        print_fn("GPIO not available, cannot run real door sensor")
        return
    
    ds1 = DS1(pin)
    ds1.setup(print_fn, mqtt_publisher, device_id)
    
    print_fn("Door sensor (REAL) started")
    
    while not stop_event.wait(1.0):
        pass
    
    GPIO.cleanup(pin)
    print_fn("Door sensor stopped")