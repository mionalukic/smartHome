import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

NUMBERS = {
    ' ':(0,0,0,0,0,0,0),
    '0':(1,1,1,1,1,1,0),
    '1':(0,1,1,0,0,0,0),
    '2':(1,1,0,1,1,0,1),
    '3':(1,1,1,1,0,0,1),
    '4':(0,1,1,0,0,1,1),
    '5':(1,0,1,1,0,1,1),
    '6':(1,0,1,1,1,1,1),
    '7':(1,1,1,0,0,0,0),
    '8':(1,1,1,1,1,1,1),
    '9':(1,1,1,1,0,1,1)
}

class Kitchen4SD:

    def __init__(self, segments, digits, refresh_ms=1):
        self.segments = segments
        self.digits = digits
        self.refresh = refresh_ms / 1000.0
        self.value = "0000"
        self.blink = False
        self.visible = True

    def setup(self):
        GPIO.setmode(GPIO.BCM)
        for s in self.segments:
            GPIO.setup(s, GPIO.OUT)
            GPIO.output(s, 0)
        for d in self.digits:
            GPIO.setup(d, GPIO.OUT)
            GPIO.output(d, 1)

    def handle_command(self, payload):
        if payload.get("command") == "display":
            self.set_value(payload.get("mmss", "0000"))
            self.blink = payload.get("blink", False)

    def run(self, stop_event):
        self.setup()

        while not stop_event.is_set():

            if self.blink:
                self.visible = not self.visible
            else:
                self.visible = True

            display_value = self.value if self.visible else "    "

            for digit in range(4):
                char = display_value[digit]
                for i in range(7):
                    GPIO.output(self.segments[i], NUMBERS[char][i])
                GPIO.output(self.digits[digit], 0)
                time.sleep(self.refresh)
                GPIO.output(self.digits[digit], 1)

            
            if self.blink:
                self.set_value("0000")

        GPIO.cleanup()
