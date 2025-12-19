import RPi.GPIO as GPIO
import time

class DPIR(object):
    def __init__(self, pin):
        self.pin = pin
        
    def setup(self):
        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.motion_detected)
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.no_motion)

    def motion_detected():
        print("You moved")
    
    def no_motion():
        print("You stopped moving")

def run_dpir_loop(dpir, stop_event):    
    dpir.setup()
    while not stop_event.wait(1.0):
        pass