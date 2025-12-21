import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

def run_dl_led(pin,interval, stop_event):

    if GPIO is None:
        print("[LED1] GPIO not available")
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)

    print("[LED1] LED (REAL) started")
    state = False

    while not stop_event.is_set():
        state = not state
        GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
        time.sleep(interval)

    GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup(pin)
    print("[LED1] LED stopped")
