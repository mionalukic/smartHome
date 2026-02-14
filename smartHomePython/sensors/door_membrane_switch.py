import RPi.GPIO as GPIO
import time

class DMS:

    KEY_MAP = [
        ["1", "2", "3", "A"],
        ["4", "5", "6", "B"],
        ["7", "8", "9", "C"],
        ["*", "0", "#", "D"]
    ]

    def __init__(self, R1, R2, R3, R4, C1, C2, C3, C4):
        self.rows = [R1, R2, R3, R4]
        self.cols = [C1, C2, C3, C4]

        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = "pi1"

    def setup(self, print_fn=print, mqtt_publisher=None, device_id="pi1"):

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id

        # rows -> output
        for row in self.rows:
            GPIO.setup(row, GPIO.OUT)
            GPIO.output(row, GPIO.HIGH)

        # columns -> input with pull-down
        for col in self.cols:
            GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def scan_key(self):

        for row_index, row_pin in enumerate(self.rows):

            GPIO.output(row_pin, GPIO.LOW)

            for col_index, col_pin in enumerate(self.cols):

                if GPIO.input(col_pin) == GPIO.HIGH:
                    key = self.KEY_MAP[row_index][col_index]
                    GPIO.output(row_pin, GPIO.HIGH)
                    return key

            GPIO.output(row_pin, GPIO.HIGH)

        return None

    def publish_key(self, key):

        if not (self.mqtt_publisher and self.mqtt_publisher.connected):
            return

        topic = f"smarthome/{self.device_id}/sensors/dms"

        data = {
            "device_id": self.device_id,
            "sensor_type": "door_membrane_switch",
            "component": "DMS",
            "key": key,
            "simulated": False,
            "timestamp": time.time()
        }

        self.mqtt_publisher.publish(topic, data, use_batch=True)

def run_dms_loop(dms, stop_event, print_fn=print, mqtt_publisher=None, device_id='pi1'):

    dms.setup(print_fn, mqtt_publisher, device_id)

    print_fn("DMS matrix scanning started")

    last_key = None

    while not stop_event.is_set():

        key = dms.scan_key()

        if key and key != last_key:
            print_fn(f"Key pressed: {key}")
            dms.publish_key(key)
            last_key = key
            time.sleep(0.3)  # debounce

        if not key:
            last_key = None

        time.sleep(0.05)

    GPIO.cleanup()
    print_fn("DMS stopped")
