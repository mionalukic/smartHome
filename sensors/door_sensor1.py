import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


def run_ds1_button(pin, stop_event, print_fn=print):
    if GPIO is None:
        print_fn("GPIO not available, cannot run real door sensor")
        return

    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def button_pressed(channel):
        print_fn("Door state: OPEN")

    GPIO.add_event_detect(
        pin,
        GPIO.FALLING,
        callback=button_pressed,
        bouncetime=200
    )

    print_fn("Door sensor (REAL) started")

    while not stop_event.is_set():
        time.sleep(0.1)

    GPIO.cleanup(pin)
    print_fn("Door sensor stopped")
