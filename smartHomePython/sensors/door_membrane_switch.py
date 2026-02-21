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
    def readLine(self, line, characters):
        GPIO.output(line, GPIO.HIGH)
        if(GPIO.input(self.cols[0]) == 1):
            self.print_fn(f"Key pressed: {characters[0]}")
            self.publish_key(characters[0])
        if(GPIO.input(self.cols[1]) == 1):
            self.print_fn(f"Key pressed: {characters[1]}")
            self.publish_key(characters[1])
        if(GPIO.input(self.cols[2]) == 1):
            self.print_fn(f"Key pressed: {characters[2]}")
            self.publish_key(characters[2])
        if(GPIO.input(self.cols[3]) == 1):
            self.print_fn(f"Key pressed: {characters[3]}")
            self.publish_key(characters[3])
        GPIO.output(line, GPIO.LOW)

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

    try:
        while not stop_event.is_set():
            dms.readLine(dms.rows[0], ["1","2","3","A"])
            dms.readLine(dms.rows[1], ["4","5","6","B"])
            dms.readLine(dms.rows[2], ["7","8","9","C"])
            dms.readLine(dms.rows[3], ["*","0","#","D"])
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nApplication stopped!")
    finally:
        GPIO.cleanup()
        print_fn("DMS stopped")



