import time
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD


class LCD(object):
    def __init__(self, i2c_address=0x27):
        self.i2c_address = i2c_address
        self.print_fn = print
        self.mqtt_publisher = None
        self.device_id = "pi1"

        self.mcp = None
        self.lcd = None

    def setup(self, print_fn=print, mqtt_publisher=None, device_id="pi1"):
        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id

        # Try both common I2C addresses
        try:
            self.mcp = PCF8574_GPIO(0x27)
        except:
            try:
                self.mcp = PCF8574_GPIO(0x3F)
            except:
                raise Exception("I2C Address Error for LCD")

        # Turn on backlight
        self.mcp.output(3, 1)

        # Create LCD
        self.lcd = Adafruit_CharLCD(
            pin_rs=0,
            pin_e=2,
            pins_db=[4, 5, 6, 7],
            GPIO=self.mcp
        )

        self.lcd.begin(16, 2)
        self.lcd.clear()

        self.print_fn("LCD ready")

    def display_message(self, line1="", line2=""):
        message = f"{line1[:16]:<16}\n{line2[:16]:<16}"

        self.print_fn(f"LCD display:\n{line1}\n{line2}")

        if self.mqtt_publisher and self.mqtt_publisher.connected:
            data = {
                "device_id": self.device_id,
                "sensor_type": "lcd_display",
                "component": "LCD",
                "line1": line1,
                "line2": line2,
                "timestamp": time.time()
            }

            topic = f"smarthome/{self.device_id}/sensors/lcd"
            self.mqtt_publisher.publish(topic, data, use_batch=True)

        self.lcd.clear()
        self.lcd.message(message)

    def clear(self):
        self.lcd.clear()

    def destroy(self):
        self.lcd.clear()


def run_lcd_loop(lcd, stop_event, print_fn=print, mqtt_publisher=None, device_id="pi1"):
    lcd.setup(print_fn, mqtt_publisher, device_id)

    print_fn("LCD loop started")

    counter = 0
    while not stop_event.is_set():
        lcd.display_message(
            f"Smart Home",
            f"Counter: {counter}"
        )
        counter += 1
        time.sleep(5)

    lcd.destroy()
    print_fn("LCD loop stopped")
