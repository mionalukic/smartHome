import time
import random 

def generate_movement(duration = 1, print_fn=print):
    print_fn(f"{time.ctime()} DOOR MOTION SENSOR detected movement")
    time.sleep(duration)
    print_fn(f"{time.ctime()} DOOR MOTION SENSOR stopped detecting movement")    
    
def run_dpir_simulator(duration, stop_event, print_fn=print):    
    while True:
        generate_movement(duration, print_fn)
        time.sleep(1)
        if stop_event.is_set():
            break