import RPi.GPIO as GPIO
import time

class DPIR(object):
    def __init__(self, pin):
        self.pin = pin
        self.print_fn = print
        
    def setup(self, print_fn):
        GPIO.setup(self.pin, GPIO.IN)
        self.print_fn = print_fn
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.motion_detected)
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.no_motion)

    def motion_detected(self):
        self.print_fn("You moved")
    
    def no_motion(self):
        self.print_fn("You stopped moving")

def run_dpir_loop(dpir, stop_event, print_fn=print):    
    dpir.setup(print_fn)
    while not stop_event.wait(1.0):
        pass