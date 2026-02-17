import RPi.GPIO as GPIO
from time import sleep, time



class RGBLED(object):
    def __init__(self, red_pin, green_pin, blue_pin):
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.blue_pin = blue_pin
        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = 'pi3_bedroom_001'

    def setUp(self, print_fn=None, mqtt_publisher=None, device_id=None):
        if GPIO is None:
            print_fn("GPIO not available, cannot setup RGB LED")
            return
        GPIO.setmode(GPIO.BCM)

        #set pins as outputs
        GPIO.setup(self.red_pin, GPIO.OUT)
        GPIO.setup(self.green_pin, GPIO.OUT)
        GPIO.setup(self.blue_pin, GPIO.OUT)
        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id

    def turnOff(self):
        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.LOW)
        GPIO.output(self.blue_pin, GPIO.LOW)
        self._publish(color="off", value=0)
        
    def white(self):
        GPIO.output(self.red_pin, GPIO.HIGH)
        GPIO.output(self.green_pin, GPIO.HIGH)
        GPIO.output(self.blue_pin, GPIO.HIGH)
        self._publish(color="white", value=1)
        
    def red(self):
        GPIO.output(self.red_pin, GPIO.HIGH)
        GPIO.output(self.green_pin, GPIO.LOW)
        GPIO.output(self.blue_pin, GPIO.LOW)
        self._publish(color="red", value=2)

    def green(self):
        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.HIGH)
        GPIO.output(self.blue_pin, GPIO.LOW)
        self._publish(color="green", value=3)
        
    def blue(self):
        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.LOW)
        GPIO.output(self.blue_pin, GPIO.HIGH)
        self._publish(color="blue", value=4)
        
    def yellow(self):
        GPIO.output(self.red_pin, GPIO.HIGH)
        GPIO.output(self.green_pin, GPIO.HIGH)
        GPIO.output(self.blue_pin, GPIO.LOW)
        self._publish(color="yellow", value=5)
        
    def purple(self):
        GPIO.output(self.red_pin, GPIO.HIGH)
        GPIO.output(self.green_pin, GPIO.LOW)
        GPIO.output(self.blue_pin, GPIO.HIGH)
        self._publish(color="purple", value=6)
        
    def lightBlue(self):
        GPIO.output(self.red_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.HIGH)
        GPIO.output(self.blue_pin, GPIO.HIGH)
        self._publish(color="light_blue", value=7)
    
    def _publish(self, color, value):
        if self.mqtt_publisher and self.mqtt_publisher.connected:
            payload = {
                "device_id": self.device_id,
                "actuator_type": "rgb_led",
                "red_pin": self.red_pin,
                "green_pin": self.green_pin,
                "blue_pin": self.blue_pin,
                "light_color": color,
                "value": value,
                "simulated": False,
                "timestamp": time()
            }

            topic = f"smarthome/{self.device_id}/actuators/rgb_led"
            self.mqtt_publisher.publish(topic, payload, use_batch=True)


def run_rgb_led_loop(rgb, stop_event, command_state, print_fn=print, mqtt_publisher=None, device_id='pi'):
    last_command = None
    try:
        rgb.setUp(print_fn, mqtt_publisher, device_id)

        while not stop_event.is_set():
            current_command = command_state["value"]

            if current_command != last_command:
                if current_command == "white":
                    rgb.white()
                elif current_command == "red":
                    rgb.red()
                elif current_command == "green":
                    rgb.green()
                elif current_command == "blue":
                    rgb.blue()
                elif current_command == "yellow":
                    rgb.yellow()
                elif current_command == "purple":
                    rgb.purple()
                elif current_command == "light_blue":
                    rgb.lightBlue()
                else:
                    rgb.turnOff()

                last_command = current_command

            sleep(0.1)  

    except Exception as e:
        print_fn(f"Error in RGB LED loop: {e}")
    finally:
        GPIO.cleanup()
