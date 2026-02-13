import RPi.GPIO as GPIO
import time

class DMS(object):
    def __init__(self,R1,R2,R3,R4,C1,C2,C3,C4):
        self.R1=R1
        self.R2=R2
        self.R3=R3
        self.R4=R4
        self.C1=C1
        self.C2=C2
        self.C3=C3
        self.C4=C4
        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = 'pi1'
        
    def setup(self, print_fn=print, mqtt_publisher=None, device_id='pi1'):
       # Initialize the GPIO pins

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.R1, GPIO.OUT)
        GPIO.setup(self.R2, GPIO.OUT)
        GPIO.setup(self.R3, GPIO.OUT)
        GPIO.setup(self.R4, GPIO.OUT)

        # Make sure to configure the input pins to use the internal pull-down resistors

        GPIO.setup(self.C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
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