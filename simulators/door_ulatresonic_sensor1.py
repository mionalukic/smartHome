import time
import random

def generate_values(initial_distance=120):
    distance = initial_distance
    MIN_DISTANCE = 10
    MAX_DISTANCE = 200

    while True:
        distance += random.randint(-3, 3)
        distance = max(MIN_DISTANCE, min(MAX_DISTANCE, distance))
        yield distance


def run_dus1_simulator(stop_event, print_fn=print):
    generator = generate_values()
    print_fn("Ultrasonic simulator started")

    while not stop_event.is_set():
        distance = next(generator)
        print_fn(f"Distance: {distance} cm")
        time.sleep(1)

    print_fn("Ultrasonic simulator stopped")
