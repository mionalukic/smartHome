import time
from .PCF8574 import PCF8574_GPIO
from .Adafruit_LCD1602 import Adafruit_CharLCD


class LCD:

    def __init__(self, settings):
        self.settings = settings
        self.cols = settings.get("cols", 16)
        self.rows = settings.get("rows", 2)
        self.i2c_address = int(settings.get("i2c_address", "0x27"), 16)
        self.backlight = settings.get("backlight", True)

        self.mcp = None
        self.lcd = None

    def setup(self, print_fn=print, mqtt_publisher=None, device_id="pi3_bedroom_001"):
        self.print_fn = print_fn
        self.mqtt_publisher = mqtt_publisher
        self.device_id = device_id

        try:
            self.mcp = PCF8574_GPIO(0x27)
        except:
            try:
                self.mcp = PCF8574_GPIO(0x3F)
            except:
                raise Exception("I2C Address Error for LCD")

        # Turn on backlight
        if self.backlight:
            self.mcp.output(3, 1)

        self.lcd = Adafruit_CharLCD(
            pin_rs=0,
            pin_e=2,
            pins_db=[4, 5, 6, 7],
            GPIO=self.mcp
        )

        self.lcd.begin(self.cols, self.rows)
        self.lcd.clear()

    def display(self, line1="", line2=""):
        line1 = line1[:self.cols]
        line2 = line2[:self.cols]
        
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
        self.lcd.message(f"{line1}\n{line2}")

    def lcd_thread_func(lcd, sensor_keys, stop_event,
        print_fn=print, dht_data=None, refresh=5):
        index = 0
        while not stop_event.is_set():
            sensor_name = sensor_keys[index]
            temp, hum = dht_data.get(sensor_name, (0.0, 0.0))

            lcd.display(
                line1=f"{sensor_name} Temp:",
                line2=f"{temp:.1f}C Hum:{hum:.1f}%"
            )

            index = (index + 1) % len(sensor_keys)
            time.sleep(refresh)

        lcd.lcd.clear()
        print_fn("LCD stopped")
