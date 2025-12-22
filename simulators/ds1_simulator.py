import time
import random

def run_ds1_simulator(stop_event):
    print("[DS1] Simulator started")

    while not stop_event.is_set():
        state = random.choice(["OPEN", "CLOSED"])
        print(f"[DS1] Door state: {state}")
        time.sleep(2)

    print("[DS1] Simulator stopped")
