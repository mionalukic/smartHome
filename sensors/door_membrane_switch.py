import RPi.GPIO as GPIO
import time

class DMS(object):
    def __init__(self, button_pin, row_pin):
        self.button_pin = button_pin
        self.row_pin = row_pin
        self.print_fn = print
        
    def setup(self, print_fn=print):
        GPIO.setup(self.row_pin, GPIO.OUT)
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

        GPIO.output(self.row_pin, GPIO.LOW)
        self.print_fn = print_fn
        GPIO.add_event_detect(self.button_pin, GPIO.BOTH,
                            callback=self.event_callback,
                            bouncetime=300)
        

    def event_callback(self, pin):
        value = GPIO.input(pin)
        self.print_fn(f"pin :: {pin}, value is {value}")

def run_dms_loop(dms, stop_event, print_fn=print):    
    dms.setup(print_fn)
    while not stop_event.wait(1.0):
        pass