import time
import random

def run_dms_simulator(stop_event, print_fn=print):
    keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "+"]
    while True:
        time.sleep(random.randrange(3, 6))
        key = random.choice(keys)
        print_fn(f"{time.ctime()} Key pressed: {key}")    

        if stop_event.is_set():
            break