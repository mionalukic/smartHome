try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

import time

class DL(object):
    def __init__(self, pin):
        self.pin = pin
        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = 'pi1'
        self.current_state = False

    def setup(self, print_fn=print, mqtt_publisher=None, device_id='pi1'):
        """Setup GPIO pins"""
        if GPIO is None:
            raise RuntimeError("GPIO not available")

        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)

        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id

    def set_state(self, state, print_fn=None, mqtt_publisher=None, device_id=None):
        if GPIO is None:
            self.print_fn("GPIO not available, cannot control LED")
            return

        if print_fn:
            self.print_fn = print_fn
        if mqtt_publisher:
            self.mqtt_publisher = mqtt_publisher
        if device_id:
            self.device_id = device_id

        self.current_state = state

        if state:
            GPIO.output(self.pin, GPIO.HIGH)
            self.print_fn("Door light turned ON")
        else:
            GPIO.output(self.pin, GPIO.LOW)
            self.print_fn("Door light turned OFF")

        if self.mqtt_publisher and self.mqtt_publisher.connected:
            data = {
                "device_id": self.device_id,
                "sensor_type": "door_light",
                "component": "DL",
                "state": state,
                "timestamp": time.time()
            }

            topic = f"smarthome/{self.device_id}/sensors/dl"
            self.mqtt_publisher.publish(topic, data, use_batch=True)

def run_dl_loop(dl, stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):
 
    dl.setup(print_fn, mqtt_publisher, device_id)

    print_fn("DL ready for state changes")

    while not stop_event.is_set():
        time.sleep(1.0)

    print_fn("DL loop stopped")
