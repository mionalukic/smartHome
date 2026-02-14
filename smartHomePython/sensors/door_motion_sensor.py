import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


class DPIR(object):
    def __init__(self, pin, component):
        self.pin = pin
        self.component = component
        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = 'pi'

    def setup(self, print_fn=print, mqtt_publisher=None, device_id='pi'):
        if GPIO is None:
            print_fn("GPIO not available, cannot setup DPIR")
            return

        GPIO.setup(self.pin, GPIO.IN)
        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id

        GPIO.add_event_detect(self.pin, GPIO.RISING,
                              callback=self.motion_detected, bouncetime=300)
        GPIO.add_event_detect(self.pin, GPIO.FALLING,
                              callback=self.no_motion, bouncetime=300)

    def motion_detected(self, channel):
        self.print_fn(f"{self.component} Motion detected")

        self._publish(state="detected", value=1)

    def no_motion(self, channel):
        self.print_fn(f"{self.component} Motion stopped")

        self._publish(state="stopped", value=0)

    def _publish(self, state, value):
        if self.mqtt_publisher and self.mqtt_publisher.connected:
            payload = {
                "device_id": self.device_id,
                "sensor_type": "door_motion_sensor",
                "component": self.component,
                "pin": self.pin,
                "state": state,
                "value": value,
                "timestamp": time.time()
            }

            topic = f"smarthome/{self.device_id}/sensors/{self.component.lower()}"
            self.mqtt_publisher.publish(topic, payload, use_batch=True)


def run_dpir_loop(dpir, stop_event, print_fn=print,
                  mqtt_publisher=None, device_id='pi'):

    dpir.setup(print_fn, mqtt_publisher, device_id)
    print_fn(f"{dpir.component} motion detection active")

    while not stop_event.wait(1.0):
        pass

    print_fn(f"{dpir.component} loop stopped")
