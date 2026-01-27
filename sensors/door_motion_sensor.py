import RPi.GPIO as GPIO
import time

class DPIR(object):
    def __init__(self, pin):
        self.pin = pin
        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = 'pi1'
        
    def setup(self, print_fn=print, mqtt_publisher=None, device_id='pi1'):
        """Setup GPIO pin and event detection"""
        GPIO.setup(self.pin, GPIO.IN)
        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id
        
        # Add event detection for motion
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.motion_detected, bouncetime=300)
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.no_motion, bouncetime=300)
    
    def motion_detected(self, channel):
        """Callback when motion is detected"""
        self.print_fn("Motion detected")
        
        # Publish to MQTT if available
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
        """Callback when motion stops"""
        self.print_fn("Motion stopped")
        
        # Publish to MQTT if available
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
    """
    Main loop for door motion sensor
    
    Args:
        dpir: DPIR instance
        stop_event: Threading event for stopping
        print_fn: Function for logging
        mqtt_publisher: Optional MQTT publisher
        device_id: Device identifier
    """
    dpir.setup(print_fn, mqtt_publisher, device_id)
    
    print_fn("DPIR motion detection active")
    
    # Keep thread alive while waiting for events
    while not stop_event.wait(1.0):
        pass
    
    print_fn("DPIR loop stopped")