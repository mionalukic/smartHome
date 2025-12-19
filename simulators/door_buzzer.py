import time
import random 

def generate_sound(duration = 1):
    print(f"{time.ctime()} DOOR BUZZER ON for {duration}s")
    time.sleep(duration)
    print(f"{time.ctime()} DOOR BUZZER OFF")    
    
def run_db_simulator(duration, stop_event):    
    while True:
        generate_sound(duration)
        time.sleep(1)
        if stop_event.is_set():
            break