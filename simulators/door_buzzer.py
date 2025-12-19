import time
import random 

def generate_sound(duration = 1, print_fn=print):
    print_fn(f"{time.ctime()} DOOR BUZZER ON for {duration}s")
    time.sleep(duration)
    print_fn(f"{time.ctime()} DOOR BUZZER OFF")    
    
def run_db_simulator(stop_event, print_fn=print):    
    while True:
        duration = random.randrange(1, 5)
        generate_sound(duration, print_fn)
        time.sleep(duration)
        if stop_event.is_set():
            break