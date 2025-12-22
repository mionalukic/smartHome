import threading
from simulators.door_sensor1 import run_ds1_simulator


def run_ds1(settings, threads, stop_event, print_fn=print):
    if settings["simulated"]:
        t = threading.Thread(
            target=run_ds1_simulator,
            args=(stop_event, print_fn)
        )
    else:
        from sensors.door_sensor1 import run_ds1_button
        t = threading.Thread(
            target=run_ds1_button,
            args=(settings["pin"], stop_event, print_fn)
        )

    t.start()
    threads.append(t)
