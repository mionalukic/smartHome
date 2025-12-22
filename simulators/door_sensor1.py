import time
import random

def run_ds1_simulator(stop_event, print_fn=print):
    print_fn("Door sensor simulator started")

    while not stop_event.is_set():
        state = random.choice(["OPEN", "CLOSED"])
        print_fn(f"Door state: {state}")
        time.sleep(2)

    print_fn("Door sensor simulator stopped")
