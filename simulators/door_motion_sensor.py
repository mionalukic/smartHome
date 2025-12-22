import time
import random 

def run_dpir_simulator(stop_event, print_fn=print):    
    while True:
        duration = random.randrange(3, 5)
        print_fn(f"{time.ctime()} Detected movement")
        time.sleep(duration)
        print_fn(f"{time.ctime()} Stopped detecting movement")    
        time.sleep(duration)
        
        if stop_event.is_set():
            break