import RPi.GPIO as GPIO
import time

class DMS(object):
    def __init__(self, button_pin, row_pin):
        self.button_pin = button_pin
        self.row_pin = row_pin
        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = 'pi1'
        
    def setup(self, print_fn=print, mqtt_publisher=None, device_id='pi1'):
        GPIO.setup(self.row_pin, GPIO.OUT)
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.output(self.row_pin, GPIO.LOW)
        
        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id
        
        GPIO.add_event_detect(
            self.button_pin, 
            GPIO.BOTH,
            callback=self.event_callback,
            bouncetime=300
        )
        
    def event_callback(self, pin):
        value = GPIO.input(pin)
        state = "pressed" if value == 0 else "released"
        
        self.print_fn(f"Pin {pin}, value is {value} ({state})")
        
        if self.mqtt_publisher and self.mqtt_publisher.connected:
            data = {
                "device_id": self.device_id,
                "sensor_type": "door_membrane_switch",
                "component": "DMS",
                "pin": pin,
                "value": value,
                "state": state,
                "timestamp": time.time()
            }
            
            topic = f"smarthome/{self.device_id}/sensors/dms"
            self.mqtt_publisher.publish(topic, data, use_batch=True)

def run_dms_loop(dms, stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):

    dms.setup(print_fn, mqtt_publisher, device_id)
    
    print_fn("DMS event detection active")
    
    while not stop_event.wait(1.0):
        pass
    
    print_fn("DMS loop stopped")