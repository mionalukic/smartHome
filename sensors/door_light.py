try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


def run_dl_led(state, pin, print_fn=print):
    if GPIO is None:
        print_fn("GPIO not available, cannot control LED")
        return

    GPIO.setup(pin, GPIO.OUT)

    if state:
        GPIO.output(pin, GPIO.HIGH)
        print_fn("Door light turned ON")
    else:
        GPIO.output(pin, GPIO.LOW)
        print_fn("Door light turned OFF")
