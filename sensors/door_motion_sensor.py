import RPi.GPIO as GPIO
import time

class DPIR(object):
    def __init__(self, pin):
        self.pin = pin
        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = 'pi1'
        
    def setup(self, print_fn=print, mqtt_publisher=None, device_id='pi1'):
        GPIO.setup(self.pin, GPIO.IN)
        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id
        
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.motion_detected, bouncetime=300)
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.no_motion, bouncetime=300)
    
    def motion_detected(self, channel):
        self.print_fn("Motion detected")
        
        if self.mqtt_publisher and self.mqtt_publisher.connected:
            data = {
                "device_id": self.device_id,
                "sensor_type": "door_motion_sensor",
                "component": "DPIR1",
                "pin": self.pin,
                "state": "detected",
                "value": 1,
                "timestamp": time.time()
            }
            
            topic = f"smarthome/{self.device_id}/sensors/dpir1"
            self.mqtt_publisher.publish(topic, data, use_batch=True)
    
    def no_motion(self, channel):
        self.print_fn("Motion stopped")
        
        if self.mqtt_publisher and self.mqtt_publisher.connected:
            data = {
                "device_id": self.device_id,
                "sensor_type": "door_motion_sensor",
                "component": "DPIR1",
                "pin": self.pin,
                "state": "stopped",
                "value": 0,
                "timestamp": time.time()
            }
            
            topic = f"smarthome/{self.device_id}/sensors/dpir1"
            self.mqtt_publisher.publish(topic, data, use_batch=True)

def run_dpir_loop(dpir, stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):

    dpir.setup(print_fn, mqtt_publisher, device_id)
    
    print_fn("DPIR motion detection active")
    
    while not stop_event.wait(1.0):
        pass
    
    print_fn("DPIR loop stopped")