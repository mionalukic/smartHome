import time
try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

#kod sa vezbi
def run_dus1_ultrasonic(trig_pin, echo_pin, stop_event):

    if GPIO is None:
        print("[DUS1] GPIO not available (simulation mode)")
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(trig_pin, GPIO.OUT)
    GPIO.setup(echo_pin, GPIO.IN)

    print("[DUS1] Ultrasonic (REAL) started")

    def get_distance():
        GPIO.output(trig_pin, False)
        time.sleep(0.2)

        GPIO.output(trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(trig_pin, False)

        pulse_start = time.time()
        pulse_end = time.time()

        timeout = time.time() + 0.04
        while GPIO.input(echo_pin) == 0:
            if time.time() > timeout:
                return None
            pulse_start = time.time()

        timeout = time.time() + 0.04
        while GPIO.input(echo_pin) == 1:
            if time.time() > timeout:
                return None
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = (pulse_duration * 34300) / 2
        return round(distance, 2)

    while not stop_event.is_set():
        distance = get_distance()
        if distance is not None:
            print(f"[DUS1] Distance: {distance} cm")
        else:
            print("[DUS1] Measurement timeout")

        time.sleep(1)

    GPIO.cleanup([trig_pin, echo_pin])
    print("[DUS1] Ultrasonic stopped")
