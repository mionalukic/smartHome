import RPi.GPIO as GPIO
from datetime import datetime
from time import sleep, time


class IRSensor:

    BUTTONS = [
        0x300ff22dd, 0x300ffc23d, 0x300ff629d, 0x300ffa857,
        0x300ff9867, 0x300ffb04f, 0x300ff6897, 0x300ff02fd,
        0x300ff30cf, 0x300ff18e7, 0x300ff7a85, 0x300ff10ef,
        0x300ff38c7, 0x300ff5aa5, 0x300ff42bd, 0x300ff4ab5,
        0x300ff52ad
    ]

    BUTTON_NAMES = [
        "LEFT", "RIGHT", "UP", "DOWN",
        "2", "3", "1", "OK",
        "4", "5", "6", "7",
        "8", "9", "*", "0", "#"
    ]

    def __init__(self, pin):
        self.pin = pin
        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = "pi3_bedroom_001"

    def setUp(self, print_fn=None, mqtt_publisher=None, device_id=None):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id

    def _publish(self, button_name, hex_value):
        if self.mqtt_publisher and self.mqtt_publisher.connected:
            payload = {
                "device_id": self.device_id,
                "sensor_type": "ir",
                "component": "IR",
                "pin": self.pin,
                "value": int(button_name),
                "hex_code": hex_value,
                "simulated": False,
                "timestamp": time()
            }

            topic = f"smarthome/{self.device_id}/sensors/ir"
            self.mqtt_publisher.publish(topic, payload, use_batch=True)

    def get_binary(self):
        num1s = 0
        binary = 1
        command = []
        previous_value = 0
        value = GPIO.input(self.pin)

        while value:
            sleep(0.0001)
            value = GPIO.input(self.pin)

        start_time = datetime.now()

        while True:
            if previous_value != value:
                now = datetime.now()
                pulse_time = now - start_time
                start_time = now
                command.append((previous_value, pulse_time.microseconds))

            if value:
                num1s += 1
            else:
                num1s = 0

            if num1s > 10000:
                break

            previous_value = value
            value = GPIO.input(self.pin)

        for (typ, tme) in command:
            if typ == 1:
                if tme > 1000:
                    binary = binary * 10 + 1
                else:
                    binary *= 10

        if len(str(binary)) > 34:
            binary = int(str(binary)[:34])

        return binary

    def convert_hex(self, binary_value):
        tmp = int(str(binary_value), 2)
        return hex(tmp)

def run_ir_loop(ir, stop_event, print_fn=print, mqtt_publisher=None, device_id=None):
    ir.setUp(print_fn, mqtt_publisher, device_id)
    while not stop_event.is_set():
        try:
            in_data = ir.convert_hex(ir.get_binary())

            for i in range(len(ir.BUTTONS)):
                if hex(ir.BUTTONS[i]) == in_data:
                    button_name = ir.BUTTON_NAMES[i]
                    ir.print_fn(f"Button pressed: {button_name}")
                    ir._publish(button_name, in_data)

        except Exception as e:
            ir.print_fn(f"Error: {e}")
