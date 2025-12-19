import RPi.GPIO as GPIO
import time

class DB(object):
    def __init__(self, pin):
        self.pin = pin

    def buzz(self, pitch, duration):
        GPIO.setup(self.pin)
        period = 1.0 / pitch
        delay = period / 2
        cycles = int(duration * pitch)
        for _ in range(cycles):
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(delay)

def run_db_loop(db, pitch, duration, stop_event):    
    while True:
        db.buzz(pitch, duration)
        time.sleep(1)
        if stop_event.is_set():
            break
