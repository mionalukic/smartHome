import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

def run_ds1_button(pin, stop_event):

    def button_pressed(channel):
        print("[DS1] Door state: OPEN")

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(
        pin,
        GPIO.FALLING,        # pritisak → LOW
        callback=button_pressed,
        bouncetime=200
    )

    print("[DS1] Button (REAL) started")

    while not stop_event.is_set():
        time.sleep(0.1)

    GPIO.cleanup(pin)
    print("[DS1] Button stopped")
