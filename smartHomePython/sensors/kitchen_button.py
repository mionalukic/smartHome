import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


class KitchenButton:
    def __init__(self, pin, component="BTN"):
        self.pin = pin
        self.component = component
        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = "pi"

    def setup(self, print_fn=print, mqtt_publisher=None, device_id="pi"):
        if GPIO is None:
            print_fn("GPIO not available, cannot setup Kitchen BTN")
            return

        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id

        GPIO.add_event_detect(
            self.pin,
            GPIO.FALLING,
            callback=self.button_pressed,
            bouncetime=300
        )

    def button_pressed(self, channel):
        self.print_fn("Kitchen BTN pressed")

        if self.mqtt_publisher and self.mqtt_publisher.connected:
            payload = {
                "device_id": self.device_id,
                "sensor_type": "kitchen_button",
                "component": self.component,
                "event": "pressed",
                "value": 1,
                "timestamp": time.time()
            }

            topic = f"smarthome/{self.device_id}/sensors/{self.component.lower()}"
            self.mqtt_publisher.publish(topic, payload, use_batch=True)


def run_kitchen_button_loop(button, stop_event, print_fn=print,
                            mqtt_publisher=None, device_id="pi"):

    button.setup(print_fn, mqtt_publisher, device_id)
    print_fn("Kitchen BTN active")

    while not stop_event.wait(1.0):
        pass

    print_fn("Kitchen BTN stopped")
