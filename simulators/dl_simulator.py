import time
import random

def run_dl_simulator(stop_event):
    print("[DL] Simulator started")

    while not stop_event.is_set():
        state = random.choice(["ON", "OFF"])
        print(f"[DL] Door light state: {state}")
        time.sleep(2)

    print("[DL] Simulator stopped")

