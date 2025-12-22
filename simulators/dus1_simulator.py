import time
import random

def generate_values(initial_distance=120):
    distance = initial_distance

    MIN_DISTANCE = 10
    MAX_DISTANCE = 200

    while True:
        distance += random.randint(-3, 3)

        if distance < MIN_DISTANCE:
            distance = MIN_DISTANCE
        if distance > MAX_DISTANCE:
            distance = MAX_DISTANCE

        yield distance


def run_dus1_simulator(stop_event):
    print("[DUS1] Simulator started")

    generator = generate_values()   

    while not stop_event.is_set():
        distance = next(generator) 
        print(f"[DUS1] Distance: {distance} cm")
        time.sleep(1)

    print("[DUS1] Simulator stopped")
