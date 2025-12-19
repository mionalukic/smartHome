import time
import random 

def generate_movement(duration = 1):
    print(f"{time.ctime()} DOOR MOTION SENSOR detected movement")
    time.sleep(duration)
    print(f"{time.ctime()} DOOR MOTION SENSOR stopped detecting movement")    
    
def run_dpir_simulator(duration, stop_event):    
    while True:
        generate_movement(duration)
        time.sleep(1)
        if stop_event.is_set():
            break